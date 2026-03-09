@echo off
set SRC=C:\Users\HP\.gemini\antigravity\brain\10ecba0b-68ff-4a82-a0b2-09fefb3689d1
set DST=C:\Users\HP\Desktop\Y3 S2\projects\E-commerce product recommendation System\Ecommerce-product-recommendation-system\frontend\public\images

mkdir "%DST%" 2>nul

for %%f in (
  headphones
  smartphone
  laptop
  smartwatch
  earbuds
  gaming_controller
  dslr_camera
  usb_cable
  phone_case
  mechanical_keyboard
  wireless_mouse
  power_bank
  tablet
  smart_tv
  wifi_router
  action_camera
  smart_speaker
) do (
  for %%g in ("%SRC%\%%f_*.png") do (
    copy "%%g" "%DST%\%%f.png" >nul
    echo Copied %%f.png
  )
)

echo.
echo All product images copied to public/images!
pause
