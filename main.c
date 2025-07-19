/*===========================================================================================================

FUNCTION: Automatic door application processes data using Python3 and MSP430F5529
CREATED: 19/06/2025 by Tran Cong Khanh(sorfware) and Ly Lam Toan(hardware) - K49 - Tu dong hoa CTU (^_^)

=============================================================================================================*/

#include <msp430f5529.h>
#include <stdbool.h>
void UART_A1_Init(void);
void Ngat_P21_Init(void);
void UART1_Send_Byte(char c);
unsigned int ReadADC12(unsigned int channel);
void P81_setup(void);
void reset(void);
void calip_LM35();
void displayLED(void);
void updateDisplay(char newNumber);
void timer_setup(void);
void start_timer(void);
void calip_cua(void);
unsigned int LEDSTATUS[] = {0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90, 0xBF, 0x9C, 0xC6};
char display[4] = {'-', '-', '-', '-'};
volatile int count_array = 0;
volatile bool array_full = false;
volatile bool security = 1; 
volatile int count = 0;
volatile bool run=0;
bool once = true;
volatile int seconds_counter = 0;
volatile bool timer_expired = false;
volatile bool changing_password = false;
int nhiet_do;
unsigned int analog_LM35, analog_cua;

void main(void){
    WDTCTL = WDTPW + WDTHOLD;   
    P3DIR |= 0xFF;
    P6DIR |= 0x0F;
    P6SEL |= BIT4 + BIT5;
    P1DIR |= BIT2 + BIT3 + BIT4 + BIT5;
    P1SEL |= BIT5;
    P1OUT &= ~(BIT2+BIT3+BIT4);
    timer_setup();
    P81_setup();
    Ngat_P21_Init();
    UART_A1_Init();
    UCA1IE |= UCRXIE;
    __bis_SR_register(GIE);
    P6OUT |= 0xFF;

    while(1){
        while(security){
          if(once){
            P2IE &= ~BIT1;
            P8OUT &= ~BIT1;
            P1OUT |= BIT4;
            P1OUT &= ~(BIT2+BIT3);
            TA0CCR4=1500;
            once=false;
          }
            displayLED();
        }
        while(run){
          if(once){
              P2IE |= BIT1;
              P8OUT |= BIT1;
              P1OUT |= BIT3;
              P1OUT &= ~(BIT2+BIT4); 
              UART1_Send_Byte('O');
              start_timer();
              once = false;
          }
          displayLED();
          if(timer_expired){
              P8OUT &= ~BIT1;
              reset();
              UART1_Send_Byte('E');
              __delay_cycles(50000);
          }
        }
        if(timer_expired){
          P8OUT &= ~BIT1;
          reset();
          UART1_Send_Byte('E');
          __delay_cycles(50000);
        }}
}
void timer_setup(void){
    TA0CTL = TASSEL_2 | MC_1 | TACLR;
    TA0CCR0 = 20000;
    TA0CCR4 =1500;
    TA0CCTL4= OUTMOD_7;
}

void P81_setup(void){
    UCSCTL6 |= XT1OFF;
    P8DIR |= BIT1;
}

void start_timer(void){
    seconds_counter = 0;
    timer_expired = false;
    TA0CCTL0 = CCIE;
}
void UART_A1_Init(void){
    P4SEL |= BIT4 | BIT5;  // Configure P4.4 (TX) and P4.5 (RX)
    UCA1CTL1 |= UCSWRST;   // Reset UCA1 
    UCA1CTL1 |= UCSSEL_2;  // Select SMCLK (1 MHz)
    UCA1BR0 = 6;  // For 9600 baudrate at 1MHz
    UCA1BR1 = 0;
    UCA1MCTL |= UCBRS_0 | UCBRF_8 | UCOS16;
    UCA1CTL1 &= ~UCSWRST;  // End reset
}

void Ngat_P21_Init(void){
    P2DIR &= ~BIT1;
    P2REN |= BIT1;
    P2OUT |= BIT1;
    P2IES |= BIT1;
    P2IFG &= ~BIT1;
}

void displayLED(void){
  for(int i=0; i<100;i++){
        P6OUT = ~0x01;
        P3OUT = LEDSTATUS[display[3] == '-' ? 10 : display[3] - '0'];
        __delay_cycles(1000);
        P6OUT = ~0x02;
        P3OUT = LEDSTATUS[display[2] == '-' ? 10 : display[2] - '0'];
        __delay_cycles(1000);
        P6OUT = ~0x04;
        P3OUT = LEDSTATUS[display[1] == '-' ? 10 : display[1] - '0'];
        __delay_cycles(1000);
        P6OUT = ~0x08;
        P3OUT = LEDSTATUS[display[0] == '-' ? 10 : display[0] - '0'];
        __delay_cycles(1000);
  }
}

void UART1_Send_Byte(char c){
    unsigned int timeout = 10000;
    while (!(UCA1IFG & UCTXIFG) && timeout--){
        if (timeout == 0) {
            return;
        }
    } UCA1TXBUF = c;
}

void updateDisplay(char newNumber){
    for(int i = 0; i < 3; i++){
        display[i] = display[i+1];
    }
    display[3] = newNumber;
}

void reset(void){
    security = 1;
    run = 0;
    P2IE &= ~BIT1;
    TA0CCTL0 &= ~CCIE;
    TA0CTL |= TACLR;
    TA0CCR4=1500;
    for(int i = 0; i < 4; i++){
        updateDisplay('-');
    }
    count = 0;
    once = true;
    P1OUT &= ~(BIT2+BIT3+BIT4);
    __bic_SR_register(GIE);
    __bis_SR_register(GIE);
}

void calip_cua(void){
  analog_cua=ReadADC12(5);
  TA0CCR4 = 1000+((analog_cua*2.5)/4095.0)*1000;
}

void calip_LM35(void){
    analog_LM35 = ReadADC12(4);
    nhiet_do =((analog_LM35*2.5)/4095.0)*100.0; // ((gia tri analog 12 bit*dien ap tham chieu)/bien do tuong tu 12bit)*100
    if(nhiet_do<100){
      int chuc, don_vi;
      chuc=nhiet_do/10;
      don_vi=nhiet_do%10;
      display[0]='0'+chuc;
      display[1]='0'+don_vi;
    }else{
      display[0]='0'+9;
      display[1]='0'+9;
    }
    display[2]='0'+11;
    display[3]='0'+12;
}

unsigned int ReadADC12(unsigned int channel){
    REFCTL0 &= ~REFMSTR;
    ADC12CTL0 = ADC12SHT0_9 | ADC12REFON | ADC12REF2_5V | ADC12ON;
    __delay_cycles(100);
    ADC12CTL1 = ADC12SHP;
    ADC12MCTL0 = ADC12SREF_1 + channel;
    if (channel < 8) P6SEL |= 1 << channel;
    if (channel == 12) P7SEL |= BIT0;
    ADC12CTL0 &= ~ADC12SC;
    ADC12CTL0 |= ADC12SC + ADC12ENC;
    while (ADC12CTL1 & ADC12BUSY) __no_operation();
    return (ADC12MEM0 & 0x0FFF);
}

#pragma vector=TIMER0_A0_VECTOR
__interrupt void Timer_A0_ISR(void){
    calip_LM35();
    calip_cua();
    if (!changing_password){
        seconds_counter++;
        if(seconds_counter >= 1500){ 
            timer_expired = true;
            UART1_Send_Byte('C');
            TA0CTL &= ~MC_1;
            TA0CCTL0 &= ~CCIE;
        }
    }
}

#pragma vector=PORT2_VECTOR
__interrupt void NGATPORT2CHAM1(void){
    UART1_Send_Byte('N');
    changing_password = true;
    P1OUT |= BIT2;
    P1OUT &= ~(BIT3+BIT4);
    // TA0CTL &= ~MC_1;
    P2IFG &= ~BIT1;
}

#pragma vector=USCI_A1_VECTOR
__interrupt void NGAT_RX(void){
    char fromPython = UCA1RXBUF;
    if(security == 1){
        if(count < 4){
            updateDisplay(fromPython);
            count++;
        } else if(count == 4){
            __delay_cycles(1000);
            for(int i=0; i < 4; i++){
                updateDisplay('-');
            }
        }
    }
    if(fromPython == 'T'){
        count = 0;
        security = 0;
        run = 1;
        for(int i=0; i < 4; i++){
            updateDisplay('-');
        }
        count = 0;
        once = true;
    }else if(fromPython == 'F'){
        for(int i = 0; i < 4; i++){
            updateDisplay('-');
        }
        count = 0;
    }
    if(fromPython == 'D'){
        changing_password = false;
        P1OUT |= BIT4;
        P1OUT &= ~(BIT2+BIT3);
        TA0CTL |= MC_1;
    }
    if(fromPython=='C'){
      reset();
      UART1_Send_Byte('E');
    }
}
