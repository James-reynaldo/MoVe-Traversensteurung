/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usbd_cdc_if.h"
#include "string.h"
#include "stdbool.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c2;

SPI_HandleTypeDef hspi2;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;

TSC_HandleTypeDef htsc;

UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */
//motor parameters
uint8_t rx_buffer[10];
uint8_t rx_indx;
uint8_t tx_buffer[100];
uint8_t transfer_cplt;
char edit_type;

volatile int period=0;
volatile int steps=0;
volatile bool direction=0;
volatile int motor=0;
MOTOR_STATE motor_state = MOTOR_STATE_REST;

int step_counter;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_I2C2_Init(void);
static void MX_SPI2_Init(void);
static void MX_TSC_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM2_Init(void);
static void MX_TIM1_Init(void);
/* USER CODE BEGIN PFP */
void performStepping(int stepDelay, bool Dir, int num_steps,  GPIO_TypeDef* dirPort, GPIO_TypeDef* stepPort, uint16_t dirPin, uint16_t stepPin);
void performStepping2(int stepDelay, bool Dir, int num_steps, int motor );

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
char *data = "Hello from CONTROLLERSTECH\n\r";

uint8_t rx_data[64];

void microDelay (uint16_t delay) // 1MHz
{
  __HAL_TIM_SET_COUNTER(&htim1, 0);
  while (__HAL_TIM_GET_COUNTER(&htim1) < delay);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_I2C2_Init();
  MX_SPI2_Init();
  MX_TSC_Init();
  MX_USART1_UART_Init();
  MX_USB_DEVICE_Init();
  MX_TIM3_Init();
  MX_TIM2_Init();
  MX_TIM1_Init();
  /* USER CODE BEGIN 2 */
  HAL_TIM_Base_Start(&htim1);
  HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
  HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
  TIM3->CNT=32768;
  TIM2->CNT=500000;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Check also static int8_t CDC_Receive_FS(uint8_t* Buf, uint32_t *Len) in USB_DEVICE/App/usbd_cdc_if.c for the code to interrupt an run Execution
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


//	   If motor is in running state
	  	    if (motor_state == MOTOR_STATE_RUN){
	  	        // Transmit current motor state over UART
	  	        sprintf(tx_buffer,"\nsteps:%d period:%d Direction:%d motor:%d\n",steps,period,direction,motor);
	  	        CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));

	  	        // Enable UART receive interrupt and perform stepping
	  	        HAL_NVIC_EnableIRQ(USART2_IRQn);
	  	        performStepping2(period, direction, steps,motor);

	  	        // Abort receive interrupt and disable UART receive interrupt
	  	        HAL_NVIC_DisableIRQ(USART2_IRQn);

	  	        // Transmit 'done' message over UART
	  	        sprintf(tx_buffer,"done\n");
	  	        CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));

	  	        if (motor == 0){
	  	        sprintf(tx_buffer,"%d\n",TIM3->CNT); // Angular encoder value
				CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));
	  	        }else if (motor==1){
	  	        	sprintf(tx_buffer,"%d\n",TIM2->CNT); // Radial encoder value
	  	        	CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));
	  	        }




	  	        // Reset receive data and set motor state to rest
	  	        memset (rx_data, '\0', 64);
	  	        motor_state = MOTOR_STATE_REST;
	  	    }

	  	    // If motor is in edit state
	  	    char *token;
	  	    if (motor_state == MOTOR_STATE_EDIT){
	  	    	if(rx_data[0]!=0){
	  	    		if(rx_data[0]!=13){ // 13= Enter Button
						// Append received data to receive buffer
						rx_buffer[rx_indx++]=rx_data[0];
					}
					else{
						// Finish receiving data and process command
						rx_buffer[rx_indx++]='!';
						rx_indx = 0;
						transfer_cplt=1;

						// Tokenize received command
						token = strtok((char*)rx_buffer,"!");
						edit_type = token[0];
						token = strtok(NULL,"!");
						int result = atoi(token);

						// Set motor parameters based on command
						if(edit_type == 'p'){
							period= result;
						}
						else if(edit_type == 's'){
							steps = result;
						}
						else if(edit_type == 'm'){
							motor = result;
						}
						else if(edit_type == 'd'){
							if (result==0){
								direction = false;
							}else{
								direction = true;
							}
						}
						if(edit_type == 'e'){
							sprintf(tx_buffer,"%d\n",TIM3->CNT); // Angular encoder value
							CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));
							sprintf(tx_buffer,"%d\n",TIM2->CNT); // Radial encoder value
							CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));

						}
						if(edit_type == 'c'){
							if (direction == true){
								sprintf(tx_buffer,"%d\n",steps); // Angular encoder value
								CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));
							} else{
								sprintf(tx_buffer,"%d\n",-steps); // Angular encoder value
								CDC_Transmit_FS((uint8_t*) tx_buffer, strlen(tx_buffer));
							}

						}

						// Set motor state to rest
						motor_state = MOTOR_STATE_REST;
					}
	  	    		memset (rx_data, '\0', 64);
	  	    	}

	  	    }

	  	    // If motor is in rest state
	  	    if (motor_state== MOTOR_STATE_REST){
	  	        // Check for specific commands and set editing mode accordingly
	  	        if (rx_data[0]=='p'){
	  	            rx_buffer[0]= 'p';
	  	            rx_buffer[1]= '!';
	  	            rx_indx = 2;
	  	            motor_state = MOTOR_STATE_EDIT;
	  	        }
	  	        else if (rx_data[0]=='s'){
	  	            rx_buffer[0]= 's';
	  	            rx_buffer[1]= '!';
	  	            rx_indx = 2;
	  	            motor_state = MOTOR_STATE_EDIT;
	  	        }
	  	        else if (rx_data[0]=='d'){
	  	            rx_buffer[0]= 'd';
	  	            rx_buffer[1]= '!';
	  	            rx_indx = 2;
	  	            motor_state = MOTOR_STATE_EDIT;
	  	        }
	  	        else if (rx_data[0]=='m'){
	  	            rx_buffer[0]= 'm';
	  	            rx_buffer[1]= '!';
	  	            rx_indx = 2;
	  	            motor_state = MOTOR_STATE_EDIT;
	  	        }
	  	      else if (rx_data[0]=='e'){
					rx_buffer[0]= 'e';
					rx_buffer[1]= '!';
					rx_indx = 2;
					motor_state = MOTOR_STATE_EDIT;
				}
	  	    else if (rx_data[0]=='c'){
					rx_buffer[0]= 'c';
					rx_buffer[1]= '!';
					rx_indx = 2;
					motor_state = MOTOR_STATE_EDIT;
				}
	  	        else if (rx_data[0]=='r'){
	  	            // Switch to run mode
	  	            motor_state = MOTOR_STATE_RUN;
	  	        }
	  	        memset (rx_data, '\0', 64);
	  	    }

	  	    // Reset receive buffer when no data is received or received data is not valid
	  	    int i;
	  	    if(rx_indx == 0 && rx_data[0]!= 0){
	  	        for(i=0; i<10; i++)
	  	            rx_buffer[i] = 0;
	  	        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
	  	    }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI|RCC_OSCILLATORTYPE_HSI48;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSI48State = RCC_HSI48_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;
  RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV1;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB|RCC_PERIPHCLK_USART1;
  PeriphClkInit.Usart1ClockSelection = RCC_USART1CLKSOURCE_PCLK1;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_HSI48;

  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief I2C2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C2_Init(void)
{

  /* USER CODE BEGIN I2C2_Init 0 */

  /* USER CODE END I2C2_Init 0 */

  /* USER CODE BEGIN I2C2_Init 1 */

  /* USER CODE END I2C2_Init 1 */
  hi2c2.Instance = I2C2;
  hi2c2.Init.Timing = 0x20303E5D;
  hi2c2.Init.OwnAddress1 = 0;
  hi2c2.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c2.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c2.Init.OwnAddress2 = 0;
  hi2c2.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c2.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c2.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c2, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c2, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C2_Init 2 */

  /* USER CODE END I2C2_Init 2 */

}

/**
  * @brief SPI2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI2_Init(void)
{

  /* USER CODE BEGIN SPI2_Init 0 */

  /* USER CODE END SPI2_Init 0 */

  /* USER CODE BEGIN SPI2_Init 1 */

  /* USER CODE END SPI2_Init 1 */
  /* SPI2 parameter configuration*/
  hspi2.Instance = SPI2;
  hspi2.Init.Mode = SPI_MODE_MASTER;
  hspi2.Init.Direction = SPI_DIRECTION_2LINES;
  hspi2.Init.DataSize = SPI_DATASIZE_4BIT;
  hspi2.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi2.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi2.Init.NSS = SPI_NSS_SOFT;
  hspi2.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_4;
  hspi2.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi2.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi2.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi2.Init.CRCPolynomial = 7;
  hspi2.Init.CRCLength = SPI_CRC_LENGTH_DATASIZE;
  hspi2.Init.NSSPMode = SPI_NSS_PULSE_ENABLE;
  if (HAL_SPI_Init(&hspi2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI2_Init 2 */

  /* USER CODE END SPI2_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 71;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 65535;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 1000001;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 5;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 5;
  if (HAL_TIM_Encoder_Init(&htim2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65535;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 5;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 5;
  if (HAL_TIM_Encoder_Init(&htim3, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief TSC Initialization Function
  * @param None
  * @retval None
  */
static void MX_TSC_Init(void)
{

  /* USER CODE BEGIN TSC_Init 0 */

  /* USER CODE END TSC_Init 0 */

  /* USER CODE BEGIN TSC_Init 1 */

  /* USER CODE END TSC_Init 1 */

  /** Configure the TSC peripheral
  */
  htsc.Instance = TSC;
  htsc.Init.CTPulseHighLength = TSC_CTPH_2CYCLES;
  htsc.Init.CTPulseLowLength = TSC_CTPL_2CYCLES;
  htsc.Init.SpreadSpectrum = DISABLE;
  htsc.Init.SpreadSpectrumDeviation = 1;
  htsc.Init.SpreadSpectrumPrescaler = TSC_SS_PRESC_DIV1;
  htsc.Init.PulseGeneratorPrescaler = TSC_PG_PRESC_DIV4;
  htsc.Init.MaxCountValue = TSC_MCV_8191;
  htsc.Init.IODefaultMode = TSC_IODEF_OUT_PP_LOW;
  htsc.Init.SynchroPinPolarity = TSC_SYNC_POLARITY_FALLING;
  htsc.Init.AcquisitionMode = TSC_ACQ_MODE_NORMAL;
  htsc.Init.MaxCountInterrupt = DISABLE;
  htsc.Init.ChannelIOs = TSC_GROUP1_IO3|TSC_GROUP2_IO3|TSC_GROUP3_IO2;
  htsc.Init.ShieldIOs = 0;
  htsc.Init.SamplingIOs = TSC_GROUP1_IO4|TSC_GROUP2_IO4|TSC_GROUP3_IO3;
  if (HAL_TSC_Init(&htsc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TSC_Init 2 */

  /* USER CODE END TSC_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 38400;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, DIR3_Pin|STEP3_Pin|DIR4_Pin|NCS_MEMS_SPI_Pin
                          |EXT_RESET_Pin|LD4_Pin|LD5_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(STEP4_GPIO_Port, STEP4_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, STEP2_Pin|DIR2_Pin|STEP_Pin|DIR_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : DIR3_Pin STEP3_Pin DIR4_Pin NCS_MEMS_SPI_Pin
                           EXT_RESET_Pin LD4_Pin LD5_Pin */
  GPIO_InitStruct.Pin = DIR3_Pin|STEP3_Pin|DIR4_Pin|NCS_MEMS_SPI_Pin
                          |EXT_RESET_Pin|LD4_Pin|LD5_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : STEP4_Pin */
  GPIO_InitStruct.Pin = STEP4_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(STEP4_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : MEMS_INT1_Pin MEMS_INT2_Pin */
  GPIO_InitStruct.Pin = MEMS_INT1_Pin|MEMS_INT2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_EVT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : B1_Pin */
  GPIO_InitStruct.Pin = B1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_EVT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : STEP2_Pin DIR2_Pin STEP_Pin DIR_Pin */
  GPIO_InitStruct.Pin = STEP2_Pin|DIR2_Pin|STEP_Pin|DIR_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
void performStepping(int stepDelay, bool Dir, int num_steps,  GPIO_TypeDef* dirPort, GPIO_TypeDef* stepPort, uint16_t dirPin, uint16_t stepPin) {


    // Set direction to clockwise
    if(Dir==true){
        HAL_GPIO_WritePin(dirPort, dirPin, GPIO_PIN_SET);
    }else{
        HAL_GPIO_WritePin(dirPort, dirPin, GPIO_PIN_RESET);
    }
    int encoder_counter = 0;
    int encoder_old;
    int encoder_new;
    bool flag = false;
    int thresCounter = 0;
    int thresDiff = 0;

    if(stepPin == STEP_Pin){
    	thresCounter = 15; // angular
    	thresDiff = 60;
    } else if (stepPin == STEP2_Pin){
    	thresCounter = 5000; // radial
    	thresDiff=1000;
    }

    // Perform steps in clockwise direction
    for (step_counter = 0; step_counter < num_steps; step_counter = step_counter + 1) {
    	if (motor_state == MOTOR_STATE_RUN){ // no key interrupt sent
    		if (stepPin == STEP_Pin){
				if(flag==false){encoder_old = TIM3->CNT;}

			}
			else if (stepPin == STEP2_Pin){
				if(flag==false){encoder_old = TIM2->CNT;}

			}
            HAL_GPIO_WritePin(stepPort, stepPin, GPIO_PIN_SET);
            microDelay(stepDelay);
            HAL_GPIO_WritePin(stepPort, stepPin, GPIO_PIN_RESET);
            microDelay(stepDelay);

            if (stepPin == STEP_Pin){
            	encoder_new = TIM3->CNT;
            }else if (stepPin == STEP2_Pin){
            	encoder_new = TIM2->CNT;
            }
            if (abs(encoder_new - encoder_old) <= thresDiff){ // if motor is not moving (motor at edge)
            	encoder_counter++;
            	flag = true;
            	if (encoder_counter == thresCounter){ // if motor still not moving after multiple steps
            		break;
            	}
            }else{ // if motor is moving (motor not at edge)
            	encoder_counter = 0;
            	flag = false;
            }

    	}
    	else{ // key interrupt sent, motor stops! (Interrupt code can be found in USB_DEVICE/usbd_cdc_if.c)
    		break;
    	}
    }

}
void performStepping2(int stepDelay, bool Dir, int num_steps , int motor) {


    switch(motor){
    case 0:
    	performStepping(stepDelay, Dir, num_steps, DIR_GPIO_Port, STEP_GPIO_Port, DIR_Pin, STEP_Pin);
    	break;
    case 1:
    	performStepping(stepDelay, Dir, num_steps, DIR2_GPIO_Port, STEP2_GPIO_Port, DIR2_Pin, STEP2_Pin);
    	break;
    case 2:
    	performStepping(stepDelay, Dir, num_steps, DIR3_GPIO_Port, STEP3_GPIO_Port, DIR3_Pin, STEP3_Pin);
    	break;
    case 3:
    	performStepping(stepDelay, Dir, num_steps, DIR4_GPIO_Port, STEP4_GPIO_Port, DIR4_Pin, STEP4_Pin);
    	break;
    }
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
