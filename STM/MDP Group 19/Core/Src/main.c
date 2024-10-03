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
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "oled.h"
#include "PID.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
#define ECHO_Port 	GPIOB
#define ECHO_Pin	GPIO_PIN_4
#define TRIG_Port	GPIOE
#define TRIG_Pin	GPIO_PIN_9
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
 ADC_HandleTypeDef hadc1;

I2C_HandleTypeDef hi2c1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;
TIM_HandleTypeDef htim8;

UART_HandleTypeDef huart3;

/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for Motor */
osThreadId_t MotorHandle;
const osThreadAttr_t Motor_attributes = {
  .name = "Motor",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for Encoder */
osThreadId_t EncoderHandle;
const osThreadAttr_t Encoder_attributes = {
  .name = "Encoder",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for IMU */
osThreadId_t IMUHandle;
const osThreadAttr_t IMU_attributes = {
  .name = "IMU",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for soundSensor */
osThreadId_t soundSensorHandle;
const osThreadAttr_t soundSensor_attributes = {
  .name = "soundSensor",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* Definitions for Show */
osThreadId_t ShowHandle;
const osThreadAttr_t Show_attributes = {
  .name = "Show",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* USER CODE BEGIN PV */
float echo =0;
float tc1, tc2;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_TIM8_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM2_Init(void);
static void MX_I2C1_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM4_Init(void);
static void MX_ADC1_Init(void);
void stop();
void forward();
void reverse();
void servomotor_right();
void servomotor_center();
void servomotor_left();
void right_turn(int angle);
void left_turn(int angle);
void gyroInit();
void writeByte(uint8_t addr, uint8_t data);
void readByte(uint8_t addr, uint8_t *data);
void delay_us(uint16_t us);
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim);
void HCSR04_Read (void);
void StartDefaultTask(void *argument);
void motorA(void *argument);
void encoder(void *argument);
void gyro_task(void *argument);
void ultrasonic_task(void *argument);
void show_task(void *argument);

/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
float speedOfSound = 0.0343/2;
//uint8_t motorA[20]; //move as global
uint8_t motorB[20]; //move as global
uint8_t Angle[20];
uint8_t dist[20];
uint8_t IRleft[20];
//Motor Global Var
int PID_DELAY = 1;
int PID_ENABLE = 0;
int PWML, PWMR;
const pwmval=2000; //Straight speed
const pwmval2=1500; //Turning speed
uint16_t pwmvalL,pwmvalR;
uint16_t pwmvalL2,pwmvalR2;
int pwm_L_f, pwm_L_b;
int pwm_R_f, pwm_R_b;
int pwm_L_div = 1, pwm_R_div = 1;
//	int offset_L, offset_R;
pwm_L_f = 1400; //Speed 2500 > 1950, 4000 > 3120, 3200 > 2500
pwm_L_b = 1625; //Speed 2500 > 2050, 4000 > 3280, 3200 > 2625
pwm_R_f = 1400; //Speed 2500 > 2050, 4000 > 3280, 3200 > 2625
pwm_R_b = 1525; //Speed 2500 > 2100, 4000 > 3360, 3200 > 2690
//Delay to achieve 10cm/s
int fwdTime=500;
int motor_dir; //Backward = -1, Stop = 0, Forward = 1
int servo_dir; //left = -1, center = 0, right = 1
double left_distance, right_distance;

//Encoder Global Var
int left_speed, right_speed;
double LEFTWHEEL_DIST;
double RIGHTWHEEL_DIST;
double full_rotation_wheel = 1250;
double circumference_wheel = 20.4;
double distance = 1200.0;

//gyroscope global var
uint8_t ICM_ADDR = 0x68;
uint8_t buff[20]; //Gyroscope buffer
double TOTAL_ANGLE = 0;
double TURNING_ANGLE = 0;
double TARGET_ANGLE = 90;

//Ultrasound Global Variables
uint32_t Echo_Val1 = 0;
uint32_t Echo_Val2 = 0;
uint32_t Difference = 0;
uint8_t Is_First_Captured = 0;
uint8_t Distance=999;
uint8_t UD=999;
int same=0;
uint16_t final_distance = 60;
int stime = 0;
double ultra_Distance  = 0; //Ultrasound distance

//IR sensor global variables
#define BUFFER_SIZE 4  // Buffer size for 10 samples

float irBufferL[BUFFER_SIZE]; // Buffer for left IR sensor
//float irBufferR[BUFFER_SIZE]; // Buffer for right IR sensor
int bufferIndex = 0;          // Current index in the buffer
float ir_distL_Avg = 0;       // Average distance for left IR sensor
//float ir_distR_Avg = 0;       // Average distance for right IR sensor
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
	uint8_t sbuf[15] = "Hello World!\n\r";
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
  MX_USART3_UART_Init();
  MX_TIM8_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  MX_I2C1_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_ADC1_Init();
  /* USER CODE BEGIN 2 */
  	OLED_Init();
    /*OLED_ShowString(10, 5, "MDP GOGO!");

    OLED_buf = "2nd lab";
    OLED_ShowString(40, 30, OLED_buf);*/
    //OLED_Refresh_Gram();
  /* USER CODE END 2 */

  /* Init scheduler */
  osKernelInitialize();

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* creation of Motor */
  MotorHandle = osThreadNew(motorA, NULL, &Motor_attributes);

  /* creation of Encoder */
  EncoderHandle = osThreadNew(encoder, NULL, &Encoder_attributes);

  /* creation of IMU */
  IMUHandle = osThreadNew(gyro_task, NULL, &IMU_attributes);

  /* creation of soundSensor */
  soundSensorHandle = osThreadNew(ultrasonic_task, NULL, &soundSensor_attributes);

  /* creation of Show */
  ShowHandle = osThreadNew(show_task, NULL, &Show_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

  /* Start scheduler */
  osKernelStart();

  /* We should never get here as control is now taken by the scheduler */
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	  HAL_GPIO_TogglePin(LED3_GPIO_Port, LED3_Pin);
	  //HAL_GPIO_TogglePin(Buzzer_GPIO_Port, Buzzer_Pin);
	  HAL_UART_Transmit(&huart3, sbuf, sizeof(sbuf), HAL_MAX_DELAY);
	  HAL_Delay(2000);

	  //HAL_GPIO_WritePin(GPIOA, LED3_Pin, GPIO_PIN_RESET);

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

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_10;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

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
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 160;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 1000;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_4) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

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
  htim2.Init.Period = 65535;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 10;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 10;
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
  sConfig.IC1Filter = 10;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 10;
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
  * @brief TIM4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_IC_InitTypeDef sConfigIC = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 16-1;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 65535;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_IC_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_RISING;
  sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
  sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
  sConfigIC.ICFilter = 0;
  if (HAL_TIM_IC_ConfigChannel(&htim4, &sConfigIC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM4_Init 2 */

  /* USER CODE END TIM4_Init 2 */

}

/**
  * @brief TIM8 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM8_Init(void)
{

  /* USER CODE BEGIN TIM8_Init 0 */

  /* USER CODE END TIM8_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM8_Init 1 */

  /* USER CODE END TIM8_Init 1 */
  htim8.Instance = TIM8;
  htim8.Init.Prescaler = 0;
  htim8.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim8.Init.Period = 7199;
  htim8.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim8.Init.RepetitionCounter = 0;
  htim8.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim8, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim8, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim8, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM8_Init 2 */

  /* USER CODE END TIM8_Init 2 */

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOE, SCLK_Pin|SDIN_Pin|RESET__Pin|DC_Pin
                          |LED3_Pin|Trig_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(Buzzer_GPIO_Port, Buzzer_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : SCLK_Pin SDIN_Pin RESET__Pin DC_Pin
                           LED3_Pin Trig_Pin */
  GPIO_InitStruct.Pin = SCLK_Pin|SDIN_Pin|RESET__Pin|DC_Pin
                          |LED3_Pin|Trig_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  /*Configure GPIO pins : AIN2_Pin AIN1_Pin BIN1_Pin BIN2_Pin */
  GPIO_InitStruct.Pin = AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : Buzzer_Pin */
  GPIO_InitStruct.Pin = Buzzer_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(Buzzer_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : INT_Pin */
  GPIO_InitStruct.Pin = INT_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(INT_GPIO_Port, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */
void stop()
{
	//Stop both wheels
	motor_dir = 0;
	__HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,0);
	__HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,0);
}

void forward()
{
	//PID
	//pwmvalR = pwmval;
	//pwmvalL = pwmval;
	motor_dir = 1;
	//Left motor
	//servomotor_center(); //Center before starting
    HAL_GPIO_WritePin(GPIOA,AIN2_Pin,GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOA,AIN1_Pin,GPIO_PIN_SET);
//	pwmval=PIDController_Update(&motorL_PID,pwmval,spdL);
	//__HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmvalL);
	__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, pwm_L_f/pwm_L_div);


	//Right motor
	HAL_GPIO_WritePin(GPIOA,BIN2_Pin,GPIO_PIN_RESET);
	HAL_GPIO_WritePin(GPIOA,BIN1_Pin,GPIO_PIN_SET);
	//__HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmvalR);
	__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, pwm_R_f/pwm_R_div);

	HAL_Delay(10);
}

void reverse()
{
	//PID
	//pwmvalR = pwmval;  //20
	//pwmvalL = pwmval; //45
	motor_dir = -1;
	//Left motor
	servomotor_center(); //Center before starting
	HAL_GPIO_WritePin(GPIOA,AIN2_Pin,GPIO_PIN_SET);
	HAL_GPIO_WritePin(GPIOA,AIN1_Pin,GPIO_PIN_RESET);
	__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, pwm_L_b/pwm_L_div);

	//Right motor
	HAL_GPIO_WritePin(GPIOA,BIN2_Pin,GPIO_PIN_SET);
	HAL_GPIO_WritePin(GPIOA,BIN1_Pin,GPIO_PIN_RESET);
	__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, pwm_R_b/pwm_R_div);

	HAL_Delay(10);

}

void servomotor_right()
{
	// default: 225
	uint32_t value = 200;
	if (htim1.Instance->CCR4 == value){
			return;
	}
	htim1.Instance->CCR4 = value;
	servo_dir = -1;
	osDelay(200);
}

void servomotor_center()
{
	// default: 150
	uint32_t value;
	if (htim1.Instance->CCR4 == 96)
		value = 145;
	else
		value = 127;
	if (htim1.Instance->CCR4 == value){
		return;
	}
	htim1.Instance->CCR4 = value;
	servo_dir = 0;
	osDelay(200);
}

void servomotor_left()
{
	// default: 107
	uint32_t value = 96;
	if (htim1.Instance->CCR4 == value){
			return;
	}
	htim1.Instance->CCR4 = value;
	servo_dir = 1;
	osDelay(200);
}

void right_turn(int angle) //Keep for debugging purpose
{
	//Prep the servomotor to right
	servomotor_right();

	osDelay(250);

	TURNING_ANGLE = 0;
	forward();
	//Start the motor
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, 3500);
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, 3500);

	while (TURNING_ANGLE > -1*angle){ //while it is still turning to the correct angle
		servomotor_right();
		osDelay(10);
	}


	//Stop the Motor are completing the turn
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, 0);
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, 0);
	stop();

	servomotor_center();
}

void left_turn(int angle) //Keep for debugging purpose
{
	//Prep the servomotor to left
	servomotor_left();

	osDelay(250);

	TURNING_ANGLE = 0;
	forward();
	//Start the motor
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, 3500);
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, 3500);

	while (TURNING_ANGLE < angle){ //while it is still turning to the correct angle
		servomotor_left();
		osDelay(10);
	}


	//Stop the Motor are completing the turn
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, 0);
	//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, 0);
	stop();

	servomotor_center();

}

void gyroInit()
{
	writeByte(0x06, 0x00);
	osDelayUntil(10);
	writeByte(0x03, 0x80);
	osDelayUntil(10);
	writeByte(0x07, 0x3F);
	osDelayUntil(10);
	writeByte(0x06, 0x01);
	osDelayUntil(10);
	writeByte(0x7F, 0x20); // go to bank 2
	osDelayUntil(10);
	writeByte(0x01, 0x2F); // config gyro, enable gyro, dlpf, set gyro to +-2000dps; gyro lpf = 3'b101
	osDelayUntil(10);
	writeByte(0x00, 0x00); // set gyro sample rate divider = 1 + 0(GYRO_SMPLRT_DIV[7:0])
	osDelayUntil(10);
	writeByte(0x01, 0x2F); // config accel, enable gyro, dlpf, set gyro to +-2000dps; gyro lpf = 3'b101
	osDelayUntil(10);
	writeByte(0x00, 0x00); // set gyro sample rate divider = 1 + 0(GYRO_SMPLRT_DIV[7:0])
	osDelayUntil(10);
	writeByte(0x7F, 0x00); // return to bank 1
	osDelayUntil(10);
	writeByte(0x07, 0x00);
	osDelayUntil(10);
}

void writeByte(uint8_t addr, uint8_t data)
{
	buff[0] = addr;
	buff[1] = data;
	HAL_I2C_Master_Transmit(&hi2c1, ICM_ADDR<<1, buff, 2, 20);
}

void readByte(uint8_t addr, uint8_t *data)
{
	buff[0] = addr;
	// Tell we want to read from the register
	HAL_I2C_Master_Transmit(&hi2c1, ICM_ADDR<<1, buff, 1, 10);
	// Read 2 byte from z dir register
	HAL_I2C_Master_Receive(&hi2c1, ICM_ADDR<<1, data, 2, 20);
}

void delay_us(uint16_t us)
{
	__HAL_TIM_SET_COUNTER(&htim4,0);  // set the counter value a 0
	while (__HAL_TIM_GET_COUNTER(&htim4) < us);  // wait for the counter to reach the us input in the parameter
}


void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
	if (htim->Channel == HAL_TIM_ACTIVE_CHANNEL_1)  // if the interrupt source is channel1
	{
		if (Is_First_Captured==0) // if the first value is not captured
		{
			Echo_Val1 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1); // read the first value
			Is_First_Captured = 1;  // set the first captured as true
			// Now change the polarity to falling edge
			__HAL_TIM_SET_CAPTUREPOLARITY(htim, TIM_CHANNEL_1, TIM_INPUTCHANNELPOLARITY_FALLING);
		}

		else if (Is_First_Captured==1)   // if the first is already captured
		{
			Echo_Val2 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);  // read second value
			__HAL_TIM_SET_COUNTER(htim, 0);  // reset the counter

			if (Echo_Val2 > Echo_Val1)
			{
				Difference = Echo_Val2-Echo_Val1;
			}

			else if (Echo_Val1 > Echo_Val2)
			{
				Difference = (0xffff - Echo_Val1) + Echo_Val2;
				//Difference = 0;
			}

			UD = (Difference * 0.034)/2;

			Is_First_Captured = 0; // set it back to false

			// set polarity to rising edge
			__HAL_TIM_SET_CAPTUREPOLARITY(htim, TIM_CHANNEL_1, TIM_INPUTCHANNELPOLARITY_RISING);
			__HAL_TIM_DISABLE_IT(&htim4, TIM_IT_CC1);
		}
	}
}

void HCSR04_Read (void)
{
	//	HAL_GPIO_WritePin(Trig_GPIO_Port, Trig_Pin, GPIO_PIN_SET);  // pull the TRIG pin HIGH
	//	delay_us(10);  // wait for 10 us
	//	HAL_GPIO_WritePin(Trig_GPIO_Port, Trig_Pin, GPIO_PIN_RESET);  // pull the TRIG pin low
	//
	//	__HAL_TIM_ENABLE_IT(&htim4, TIM_IT_CC1);

	HAL_GPIO_WritePin(Trig_GPIO_Port, Trig_Pin, GPIO_PIN_SET);  // pull the TRIG pin HIGH
	delay_us(10);  // wait f or 10 us
	HAL_GPIO_WritePin(Trig_GPIO_Port, Trig_Pin, GPIO_PIN_RESET);  // pull the TRIG pin low

	__HAL_TIM_ENABLE_IT(&htim4, TIM_IT_CC1);
}
/* USER CODE END 4 */

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN 5 */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END 5 */
}

/* USER CODE BEGIN Header_motorA */
/**
* @brief Function implementing the Motor thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_motorA */
void motorA(void *argument)
{
  /* USER CODE BEGIN motorA */
	//uint16_t pwmVal =0;

	HAL_TIM_PWM_Start(&htim8,TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim8,TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim1,TIM_CHANNEL_4);
	servomotor_center();
	forward();
	osDelay(2000);
	right_turn(TARGET_ANGLE);
	while (1){
		if (LEFTWHEEL_DIST >= distance || RIGHTWHEEL_DIST >= distance) stop();
		if (TURNING_ANGLE >= TARGET_ANGLE) servomotor_center();
	}

	/*int pwm_L_f, pwm_L_b;
	int pwm_R_f, pwm_R_b;
	int pwm_L_div = 1, pwm_R_div = 1;
	//	int offset_L, offset_R;
	pwm_L_f = 2400; //Speed 2500 > 1950, 4000 > 3120, 3200 > 2500
	pwm_L_b = 2625; //Speed 2500 > 2050, 4000 > 3280, 3200 > 2625
	pwm_R_f = 2625; //Speed 2500 > 2050, 4000 > 3280, 3200 > 2625
	pwm_R_b = 2690; //Speed 2500 > 2100, 4000 > 3360, 3200 > 2690*/		//move to global

	struct PIDController motor_LF_PID, motor_RF_PID, motor_LB_PID, motor_RB_PID;

	MotorPIDController_Init(&motor_LF_PID);
	MotorPIDController_Init(&motor_RF_PID);
	MotorPIDController_Init(&motor_LB_PID);
	MotorPIDController_Init(&motor_RB_PID);

	uint32_t tick = HAL_GetTick();
	uint32_t pid_time_start = 0;
	int ANGLE_OFFSET;
//	RX_FLAG = 1;
//	RX_MOTOR = 'F';
//	RX_SERVO = 'C';
//	RX_MAG = 30;
	/* Infinite loop */
	for(;;)
	{
		//clockwise
		/*while(pwmVal<4000){
		  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_SET);
		  HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_RESET);
		  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
		  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET);
		  pwmVal++;
		  __HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, pwmVal); //modify comparison value for the duty cycle
		  __HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, pwmVal);
		  osDelay(10);
	  }
	  //anticlockwise
	  while(pwmVal>0){
		  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
		  HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET);
		  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
		  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET);
		  pwmVal--;
		  __HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, pwmVal);
		  __HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, pwmVal);
		  osDelay(10);
	  }*/
		if (HAL_GetTick() - tick > 100L){
			//Calculate wheel speed change from turning
//			if (servo_dir != 0){
//				if (servo_dir == -1) {pwm_L_div = 2; pwm_R_div = 1;}
//				if (servo_dir == 1) {pwm_L_div = 1; pwm_R_div = 2;}
//			}
//			else {pwm_L_div = 1; pwm_R_div = 1;}
			//Calculate deviation
			if (motor_dir != 0 && servo_dir == 0){
				ANGLE_OFFSET = 3*((int)3*(TARGET_ANGLE - TOTAL_ANGLE));
				if (ANGLE_OFFSET >= 10) ANGLE_OFFSET = 10;
				if (ANGLE_OFFSET <= -10) ANGLE_OFFSET = -10;
			}
			//Control PID enable
			if (PID_DELAY == 1){
				pid_time_start = HAL_GetTick();
				PID_DELAY = 0;
			}
			if (PID_ENABLE == 0 && (HAL_GetTick() - pid_time_start > 400L)){
				PID_ENABLE = 1;
			}
			//Control motor
			if (motor_dir == 1){
				//Start the motor
				//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, pwm_L_f/pwm_L_div);
				//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, pwm_R_f/pwm_R_div);		//move to forward();
				//				if (servo_dir == 0) servomotor_set(SERVO_CENTER-ANGLE_OFFSET);
				//ADD PID CONTROL
				if (PID_ENABLE == 1){
					pwm_L_f = pwm_L_div*PIDController_Update(&motor_LF_PID, left_speed, 3200/pwm_L_div, pwm_L_f/pwm_L_div);
					pwm_R_f = pwm_R_div*PIDController_Update(&motor_RF_PID, right_speed, 3200/pwm_R_div, pwm_R_f/pwm_R_div);
				}
				//display to OLED
				PWML = pwm_L_f/pwm_L_div;
				PWMR = pwm_R_f/pwm_R_div;
			}
			else if (motor_dir == -1){
				//Start the motor
				//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_1, pwm_L_b/pwm_L_div);
				//__HAL_TIM_SetCompare(&htim8, TIM_CHANNEL_2, pwm_R_b/pwm_R_div);		///move to reverse();
				//				if (servo_dir == 0) servomotor_set(SERVO_CENTER+ANGLE_OFFSET);
				//ADD PID CONTROL
				if (PID_ENABLE == 1){
					pwm_L_b = pwm_L_div*PIDController_Update(&motor_LB_PID, left_speed, 3200/pwm_L_div, pwm_L_b/pwm_L_div);
					pwm_R_b = pwm_R_div*PIDController_Update(&motor_RB_PID, right_speed, 3200/pwm_R_div, pwm_R_b/pwm_R_div);
				}
				//Display to OLED
				PWML = pwm_L_b/pwm_L_div;
				PWMR = pwm_R_b/pwm_R_div;
			}
			else {
				PWML = 0;
				PWMR = 0;
				PID_ENABLE = 0;
				ANGLE_OFFSET = 0;
				//				turning_prev = TOTAL_ANGLE-TARGET_ANGLE;
				//				deviation_prev = 0;
			}
			tick = HAL_GetTick();
		}
		osDelay(10);

  }
  /* USER CODE END motorA */
}

/* USER CODE BEGIN Header_encoder */
/**
* @brief Function implementing the Encoder thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_encoder */
void encoder(void *argument)
{
  /* USER CODE BEGIN encoder */
  /* Infinite loop */
	HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);

	int cnt1A, cnt2A;
	int cnt1B, cnt2B;
	int diffA = 0;
	int diffB = 0;
	uint32_t tick, cur_tick, T;
	uint16_t dirA, dirB;

	LEFTWHEEL_DIST = 0;
	RIGHTWHEEL_DIST = 0;
	cnt1A = __HAL_TIM_GET_COUNTER(&htim2);
	cnt1B = __HAL_TIM_GET_COUNTER(&htim3);
	tick = HAL_GetTick();

  for(;;)
  {
	  cur_tick = HAL_GetTick();
	  if (cur_tick - tick > 50L){ //every 0.05 second
	  		  cnt2A = __HAL_TIM_GET_COUNTER(&htim2);
	  		  cnt2B = __HAL_TIM_GET_COUNTER(&htim3);
	  		  //Left encoder
	  		  if(__HAL_TIM_IS_TIM_COUNTING_DOWN(&htim2)){
	  			  if(cnt2A <= cnt1A){
	  				  diffA = cnt1A - cnt2A;
	  			  }
	  			  else {
	  				  diffA = (65535 - cnt2A) + cnt1A; //handle overflow situation
	  			  }
	  			  //dir_L = 1;
	  		  }
	  		  else {
	  			  if(cnt2A >= cnt1A){
	  				  diffA = cnt2A - cnt1A;
	  			  }
	  			  else {
	  				  diffA = (65535 - cnt1A) + cnt2A;
	  			  }
	  			  //dir_L = -1;
	  		  }
	  		  //Right encoder
	  		  if(__HAL_TIM_IS_TIM_COUNTING_DOWN(&htim3)){
	  			  if(cnt2B <= cnt1B){
	  				  diffB = cnt1B - cnt2B;
	  			  }
	  			  else {
	  				  diffB = (65535 - cnt2B) + cnt1B; //handle overflow situation
	  			  }
	  			  //dir_R = -1;
	  		  }
	  		  else {
	  			  if(cnt2B >= cnt1B){
	  				  diffB = cnt2B - cnt1B;
	  			  }
	  			  else {
	  				  diffB = (65535 - cnt1B) + cnt2B;
	  			  }
	  			  //dir_R = 1;
	  		  }
		  T = cur_tick - tick;

		  //Show speed in ticks/s
		  //left_speed = diffA * (1000/T);
		  //right_speed = diffB * (1000/T);

		  //Calculate distance traveled
		  //distInt_L += left_diff * dir_L;
		  //distInt_R += right_diff * dir_R;
		  LEFTWHEEL_DIST += diffA/full_rotation_wheel*circumference_wheel;
		  RIGHTWHEEL_DIST += diffB/full_rotation_wheel*circumference_wheel;
		  //		  dirA = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim2);
		  //		  dirB = __HAL_TIM_IS_TIM_COUNTING_DOWN(&htim3);
		  //sprintf(motorA, "direction:%5d\0", motor_dir);
		  //OLED_ShowString(10,40,motorA); //move to show task
		  cnt1A = __HAL_TIM_GET_COUNTER(&htim2);
		  cnt1B = __HAL_TIM_GET_COUNTER(&htim3);
		  tick = HAL_GetTick();
		  //OLED_Refresh_Gram();
	  }
    osDelay(1);
  }
  /* USER CODE END encoder */
}

/* USER CODE BEGIN Header_gyro_task */
/**
* @brief Function implementing the IMU thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_gyro_task */
void gyro_task(void *argument)
{
  /* USER CODE BEGIN gyro_task */
  /* Infinite loop */
	//uint8_t Angle[20];
	//uint8_t motorB[20];
	double offset = 7.848882995;//High power offset 7.85 //Low power offset 7.8475
	double angle;
	for(;;)
	{
		uint8_t val[2] = {0, 0};
		int16_t angular_speed = 0;

		uint32_t tick = 0;
		gyroInit();

		tick = HAL_GetTick();
		osDelayUntil(10);

		for (;;)
		{

			osDelay(10);
			if (HAL_GetTick() - tick >= 50L)
			{
				readByte(0x37, val);
				angular_speed = (val[0] << 8) | val[1];

				//	      if (motor_dir == 0){
				//	    	  offset = (offset-(double)(angular_speed))/2;
				//	      }

				angle = ((double)(angular_speed)+offset) * ((HAL_GetTick() - tick) / 16400.0);
				//	      if (motor_dir == 0) angle = 0;
				TOTAL_ANGLE += angle;
				TURNING_ANGLE += angle;

				// prevSpeed = angular_speed;
				if (TOTAL_ANGLE >= 720)
				{
					TOTAL_ANGLE -= 720;
				}
				if (TOTAL_ANGLE <= -720)
				{
					TOTAL_ANGLE += 720;
				}
				//	      sprintf(OLED_Row_1, "OFSET: %6d\0", (int)((offset*10000)));
				//sprintf(Angle, "ANGLE: %6d\0", (int)(TOTAL_ANGLE));
				//sprintf(OLED_Row_5, "A_100: %6d\0", (int)(100*TOTAL_ANGLE));

				tick = HAL_GetTick();
			}
		}
		osDelay(1);
	}
  /* USER CODE END gyro_task */
}

/* USER CODE BEGIN Header_ultrasonic_task */
/**
* @brief Function implementing the soundSensor thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_ultrasonic_task */
void ultrasonic_task(void *argument)
{
  /* USER CODE BEGIN ultrasonic_task */
  /* Infinite loop */
	HAL_TIM_IC_Start_IT(&htim4, TIM_CHANNEL_1);
	int s1=0;
	int s2=0;
	int s3=0;
	int s1c=0;
	int s2c=0;
	int s3c=0;
	//uint8_t dist[20];

	for(;;)
	{
		osDelay(5);
		HAL_ADC_Start(&hadc1);
		//HAL_ADC_Start(&hadc2);
		HAL_ADC_PollForConversion(&hadc1, 1); // trivial waiting time, dont bother with dma or whatever
		uint32_t IR = HAL_ADC_GetValue(&hadc1);
		//HAL_ADC_PollForConversion(&hadc2, 1); // trivial waiting time, dont bother with dma or whatever
		//uint32_t IR2 = HAL_ADC_GetValue(&hadc2);
		HAL_ADC_Stop(&hadc1);
		//HAL_ADC_Stop(&hadc2);
		float volt = (float) (IR * 5) / 4095;
		irBufferL[bufferIndex] = roundf(29.988 * pow(volt, -1.173));
		//volt = (float) (IR2 * 5) / 4095;
		//irBufferR[bufferIndex] = roundf(29.988 * pow(volt, -1.173));


		float sumL = 0, sumR = 0;
		for (int i = 0; i < BUFFER_SIZE; i++) {
			sumL += irBufferL[i];
			//sumR += irBufferR[i];
		}
		for(int sc=0;sc<30;sc++)
		{
			HCSR04_Read();
			s1 = UD;
			if(UD==s1)
			{
				s1c++;
			}
			else if(UD!=s1)
			{
				s2 = UD;
				s2c++;
			}
			else if(UD!=s1 && UD!=s2)
			{
				s3 = UD;
				s3c++;
			}
		}
		if(s1c>s2c && s1c>s3c)
		{
			Distance=s1;
		}
		else if(s2c>s1c && s2c>s3c)
		{
			Distance=s2;
		}
		else if(s3c>s1c && s3c>s2c)
		{
			Distance=s3;
		}
		//sprintf(dist, "DIST: %5d CM", Distance);
		//OLED_ShowString(10,50,dist);
		ir_distL_Avg = sumL / BUFFER_SIZE;
		//ir_distR_Avg = sumR / BUFFER_SIZE;

		bufferIndex = (bufferIndex + 1) % BUFFER_SIZE; // Update buffer index
		osDelay(10);
	}
  /* USER CODE END ultrasonic_task */
}

/* USER CODE BEGIN Header_show_task */
/**
* @brief Function implementing the Show thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_show_task */
void show_task(void *argument)
{
  /* USER CODE BEGIN show_task */
	uint8_t motorA[20];
  /* Infinite loop */
  for(;;)
  {
	  sprintf(motorA, "DST L: %5d\0", (int)LEFTWHEEL_DIST);
	  sprintf(motorB, "DST R: %5d\0", (int)RIGHTWHEEL_DIST);
	  sprintf(Angle, "ANGLE: %6d\0", (int)(TURNING_ANGLE));
	  sprintf(dist, "DIST: %5d CM", Distance);
	  sprintf(IRleft, "IR_L: %5d\0", (int)ir_distL_Avg);

	  OLED_ShowString(0,0,motorA);	//move to show task
	  OLED_ShowString(0,10,motorB);	//move to show task
	  OLED_ShowString(0,20,Angle);
	  OLED_ShowString(10,30,dist);
	  OLED_ShowString(10,40,IRleft);
	  OLED_Refresh_Gram();
  }
  osDelay(1);
  /* USER CODE END show_task */
}

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