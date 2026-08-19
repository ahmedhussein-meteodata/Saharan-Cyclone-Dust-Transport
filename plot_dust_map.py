import os
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 1. مسارات الملفات وإنشاء فولدر للحفظ
file_surface = r"F:\DATA\MSLP_U_V.nc"
file_dust = r"F:\DATA\Dust_cams_4d_final.nc"
output_dir = r"F:\DATA\maps_output"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. فتح البيانات
ds_surf = xr.open_dataset(file_surface)
ds_dust = xr.open_dataset(file_dust, decode_times=False)

# تحويل الضغط الجوي إلى hPa
msl_hpa = ds_surf['msl'] / 100.0  

# حساب إجمالي تركيز الغبار عند مستوى 1000 hPa
total_dust = (ds_dust['aermr04'] + ds_dust['aermr05'] + ds_dust['aermr06']).sel(pressure_level=1000)

# تعديل الفترة الزمنية: من 11 مارس إلى 16 مارس (كل 12 ساعة)
start_date = pd.Timestamp("2026-03-11 00:00:00")
end_date = pd.Timestamp("2026-03-16 12:00:00")

# إنشاء السلسلة الزمنية المطلوبة
target_times = pd.date_range(start=start_date, end=end_date, freq="12h")

#  تحديد قائمة الألوان الخمسة الموجودة بالصورة بالضبط (من الأصفر للغمّاق)
cmap_colors = ['#ffffff', '#fdb837', '#e66101', '#d7191c', '#990000', '#500000']
custom_cmap = mcolors.ListedColormap(cmap_colors)
#  تحديد حدود القيم لكل لون (0.5، 1.5، 2.5، 3.5، 4.5)
levels = [0.0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
norm = mcolors.BoundaryNorm(levels, custom_cmap.N)

# 4. الـ Loop للرسم الحركي
for idx, current_time in enumerate(target_times):

    time_offset_hours = int((current_time - pd.Timestamp("2026-03-10 00:00:00")).total_seconds() // 3600)
    i = time_offset_hours // 12  # الخطوة المناظرة في الـ forecast_reference_time
    
    # استخراج داتا الغبار للخطوة الحالية
    dust_step = total_dust.isel(forecast_reference_time=i)
    
    # حساب الوقت الحالي
    time_str = current_time.strftime("%Y-%b-%d %H:%M UTC")

    # اختيار الضغط الجوي المناظر
    msl_step = msl_hpa.sel(valid_time=current_time, method='nearest')

    # إنشاء الشكل
    fig = plt.figure(figsize=(12, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # تحديد النطاق الجغرافي لشمال إفريقيا
    ax.set_extent([-1, 51, 14, 41], crs=ccrs.PlateCarree())

    # إضافة المعالم الجغرافية
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, color='black')                # رسم خطوط السواحل
    ax.add_feature(cfeature.BORDERS, linestyle='-', linewidth=0.4, color='black')   # رسم حدود الدول
    ax.add_feature(cfeature.LAND, facecolor='none')                                 # رسم خلفيه ارضيه شفافه
    
    # رسم شبكه الاحداثيات (أرقام فقط بدون خطوط )
    grid = ax.gridlines(draw_labels=True, linewidth=0, color='none')
    grid.top_labels = False                                                         # إخفاء الأرقام من الأعلى
    grid.right_labels = False                                                       # إخفاء الأرقام من اليمين
    grid.xlabel_style = {'size': 10, 'color': 'black'}                              # تظبيط خط أرقام الطول
    grid.ylabel_style = {'size': 10, 'color': 'black'}                              # تظبيط خط أرقام العرض

    #  رسم تركيز الغبار (Shading)
    dust_plot = ax.contourf(dust_step.longitude, dust_step.latitude, dust_step * 1e6,
                        levels=levels, cmap=custom_cmap, norm=norm,
                        extend='both', transform=ccrs.PlateCarree())

    # cbar = plt.colorbar(dust_plot, ax=ax, orientation='horizontal', pad=0.06, shrink=0.55, aspect=25)

    # رسم خطوط الضغط الجوي (الكونتور)
    contours = ax.contour(msl_step.longitude, msl_step.latitude, msl_step,
                          transform=ccrs.PlateCarree(), colors='black', levels=14, linewidths=1)
    plt.clabel(contours, inline=True, fontsize=7, fmt='%1.0f') 

    # عنوان الخريطة
    plt.title(time_str, fontsize=13, fontweight="bold", pad=10)

    # حفظ الصورة
    file_name = f'dust_map_{current_time.strftime("%Y-Mar-%d_%H")}.png'
    save_path = os.path.join(output_dir, file_name)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()

    print(f"تم حفظ الخريطة رقم {i+1}: {time_str}")