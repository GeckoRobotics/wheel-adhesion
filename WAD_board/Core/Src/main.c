/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2023 STMicroelectronics.
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

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

#define DATA_SIZE (uint16_t)4 // bytes
#define MEM_ADDR_SIZE (uint16_t)2 // bytes
#define TIMEOUT (uint32_t)1000

// Sensor I2C Addresses
#define I2C_ADDR_2000_top (uint16_t)108 // +-2000 G sensor (U5)
#define I2C_ADDR_2000_bottom (uint16_t)108

/* Debug Exception and Monitor Control Register base address */
#define DEMCR                 *((volatile uint32_t*) 0xE000EDFCu)

/* ITM register addresses */
#define ITM_STIMULUS_PORT0    *((volatile uint32_t*) 0xE0000000u)
#define ITM_TRACE_EN          *((volatile uint32_t*) 0xE0000E00u)

/* Override low-level _write system call */
int _write(int file, char *ptr, int len)
{
	(void) file;
    int DataIdx;
    for (DataIdx = 0; DataIdx < len; DataIdx++)
    {
        ITM_SendChar(*ptr++);
    }
    return len;
}

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_I2C1_Init(void);
/* USER CODE BEGIN PFP */

static void hall_sensor_init(uint16_t dev_address);
static int16_t convert_8_to_16(uint8_t dataFirst, uint8_t dataSecond);
static int16_t single_read_component_field(uint16_t dev_address, uint8_t axis);
static void transmit_component_fields_USB(int32_t x1, int32_t y1, int32_t z1, int32_t x2, int32_t y2, int32_t z2, int32_t x3, int32_t y3, int32_t z3);

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
	// Enable TRCENA
	DEMCR |= (1 << 24);
	// Enable stimulus port 0
	ITM_TRACE_EN |= ( 1 << 0);

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
  MX_I2C1_Init();
  MX_USB_DEVICE_Init();
  /* USER CODE BEGIN 2 */

  // initialize all hall-effect sensors
  hall_sensor_init(I2C_ADDR_2000_top);
  hall_sensor_init(I2C_ADDR_2000_bottom);

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	// Read component fields from top ALS31313KLEATR-2000
	int32_t x_2000 = single_read_component_field(I2C_ADDR_2000_top, 0);
	int32_t y_2000 = single_read_component_field(I2C_ADDR_2000_top, 1);
	int32_t z_2000 = single_read_component_field(I2C_ADDR_2000_top, 2);

  // Read component fields from bottom ALS31313KLEATR-2000
	int32_t x_2000 = single_read_component_field(I2C_ADDR_2000_bottom, 0);
	int32_t y_2000 = single_read_component_field(I2C_ADDR_2000_bottom, 1);
	int32_t z_2000 = single_read_component_field(I2C_ADDR_2000_bottom, 2);

	// send data to USB host
	transmit_component_fields_USB(x_500, y_500, z_500, x_1000, y_1000, z_1000, x_2000, y_2000, z_2000);

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
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB|RCC_PERIPHCLK_I2C1;
  PeriphClkInit.I2c1ClockSelection = RCC_I2C1CLKSOURCE_SYSCLK;
  PeriphClkInit.USBClockSelection = RCC_USBCLKSOURCE_PLL;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
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
  hi2c1.Init.Timing = 0x2010091A;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c1, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c1, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

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
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, LED_G_Pin|LED_B_Pin|LED_R_Pin, GPIO_PIN_SET);

  /*Configure GPIO pins : LED_G_Pin LED_B_Pin LED_R_Pin */
  GPIO_InitStruct.Pin = LED_G_Pin|LED_B_Pin|LED_R_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/**
 * @brief Send component B-field values from three sensors to USB host device
 * @param x1: x-component for ALS31313KLEATR-500
 * @param y1: y-component for ALS31313KLEATR-500
 * @param z1: z-component for ALS31313KLEATR-500
 * @param x2: x-component for ALS31313KLEATR-1000
 * @param y2: y-component for ALS31313KLEATR-1000
 * @param z2: z-component for ALS31313KLEATR-1000
 * @param x3: x-component for ALS31313KLEATR-2000
 * @param y3: y-component for ALS31313KLEATR-2000
 * @param z3: z-component for ALS31313KLEATR-2000
 * @retval None
 */
static void transmit_component_fields_USB(int32_t x1, int32_t y1, int32_t z1, int32_t x2, int32_t y2, int32_t z2)
{
	uint8_t *x1_vals = (uint8_t *)&x1;
	uint8_t *y1_vals = (uint8_t *)&y1;
	uint8_t *z1_vals = (uint8_t *)&z1;

	uint8_t *x2_vals = (uint8_t *)&x2;
	uint8_t *y2_vals = (uint8_t *)&y2;
	uint8_t *z2_vals = (uint8_t *)&z2;

	uint8_t buffer[24] = {0};

	for (uint8_t i = 0; i < sizeof(buffer); ++i)
	{
		if (i <= 3)
		{
			buffer[i] = x1_vals[3 - i];
		}

		else if ((i >= 4) & (i <= 7))
		{
			buffer[i] = y1_vals[7 - i];
		}

		else if ((i >= 8) & (i <= 11))
		{
			buffer[i] = z1_vals[11 - i];
		}

		else if ((i >= 12) & (i <= 15))
		{
			buffer[i] = x2_vals[15 - i];
		}

		else if ((i >= 16) & (i <= 19))
		{
			buffer[i] = y2_vals[19 - i];
		}

		else
		{
			buffer[i] = z2_vals[23 - i];
		}
	}

	CDC_Transmit_FS(buffer, sizeof(buffer));
	HAL_Delay(300);
}

/**
 * @brief Hall Effect Sensor Initialization Function
 * @param dev_address: 7-bit I2C device address
 * @retval None
 */
static void hall_sensor_init(uint16_t dev_address)
{
	// enter customer access code to enable writing to volatile registers
	uint8_t access_code[4] = {0x2C, 0x41, 0x35, 0x34};
	HAL_I2C_Mem_Write(&hi2c1, dev_address << 1, 0x35, I2C_MEMADD_SIZE_8BIT, access_code, DATA_SIZE, TIMEOUT);
	HAL_Delay(1000);

  if (dev_address != 0)
  {
    // Enables X, Y, and Z channels
	  // Sets hall mode to 00 and BW select to 000
	  // BW Select = 000 corresponds with a three channel update rate of 2 kHz
    uint8_t init_data[4] = {0x00, 0x00, 0x01, 0xC0};
    HAL_I2C_Mem_Write(&hi2c1, dev_address << 1, 0x02, I2C_MEMADD_SIZE_8BIT, init_data, DATA_SIZE, TIMEOUT);
    HAL_Delay(1000);
  }

  else
  {
    // Enables X, Y, and Z channels
	  // Sets hall mode to 00 and BW select to 000
	  // BW Select = 000 corresponds with a three channel update rate of 2 kHz
    // Sets "Disable Slave ADC" to 1 to use I2C address set in EEPROM
    uint8_t init_data[4] = {0x00, 0x02, 0x01, 0xC0};
    HAL_I2C_Mem_Write(&hi2c1, dev_address << 1, 0x02, I2C_MEMADD_SIZE_8BIT, init_data, DATA_SIZE, TIMEOUT);
    HAL_Delay(1000);
  }
	
	
}

/**
 * @brief Takes two 8 bit values and turns it into a 16 bit value
 * @param dataFirst: First half of binary value
 * @param dataSecond: Second half of binary value
 * @retval dataBoth: uint16_t of combined binary value
 */
static int16_t convert_8_to_16(uint8_t data_first, uint8_t data_second)
{
    int16_t data_both = 0x0000;
    data_both = data_first;
    data_both = data_both << 8;
    data_both |= data_second;
    return data_both;
}

/**
 * @brief Gets field for the x, y, or z axis from a selected sensor
 * @param dev_address: 7-bit I2C device address
 * @param axis: select 0, 1, 2 corresponding to x, y, z, axis
 * @retval b_field: component field
 */
static int16_t single_read_component_field(uint16_t dev_address, uint8_t axis)
{
	uint8_t data[8] = {0};
	uint8_t Msbs[3] = {0};
	uint8_t Lsbs[2] = {0};
	int16_t b_field = 0;
	HAL_I2C_Mem_Read(&hi2c1, dev_address << 1, 0x28, I2C_MEMADD_SIZE_8BIT, data, DATA_SIZE * 2, TIMEOUT); // read MSBs
	// HAL_Delay(150);

	// populate MSBs
	for (uint8_t i = 0; i < 3; ++i)
	{
		Msbs[i] = data[i];
	}

	// populate LSBs
	for (uint8_t i = 0; i < 2; ++i)
	{
		Lsbs[i] = data[i + 5];
	}

	if (axis == 0) // x-axis selected
	{
		uint8_t mask = 0x0F;
		uint8_t msb = Msbs[0]; // extract MSBs
		uint8_t lsb = Lsbs[0] & mask; // extract LSBs
		b_field = convert_8_to_16(msb, (lsb << 4)); // combine MSBs and LSBs into 12 bit value
	}

	else if (axis == 1) // y-axis selected
	{
		uint8_t mask = 0xF0;
		uint8_t msb = Msbs[1];
		uint8_t lsb = Lsbs[1] & mask;
		b_field = convert_8_to_16(msb, lsb);
	}

	else // z-axis selected (axis == 2)
	{
		uint8_t mask = 0x0F;
		uint8_t msb = Msbs[2];
		uint8_t lsb = Lsbs[1] & mask;
		b_field = convert_8_to_16(msb, (lsb << 4));
	}

	return (b_field >> 4); // right align 12 bit B-field
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
