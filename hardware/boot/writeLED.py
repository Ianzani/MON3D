import sys
import lgpio

led_pin = int(sys.argv[1])
led_val = int(sys.argv[2])

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, led_pin)
lgpio.gpio_write(h, led_pin, led_val)
lgpio.gpiochip_close(h)