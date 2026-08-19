import glob
import math
import os
from PIL import Image, ImageDraw, ImageFont

# -------------------------------------------------------------------------
# 1. إعداد المسارات والملفات
# -------------------------------------------------------------------------
image_dir = r"F:\DATA\maps_output"  # مجلد الخرائط
output_filename = r"F:\DATA\maps_output\Saharan_Cyclone_Vertical_Panel12.png"

# جلب الصور المحددة مرتبة زمنياً
image_files = sorted(glob.glob(os.path.join(image_dir, "dust_map_*.png")))
num_images = len(image_files)

if num_images == 0:
    print("Error: No images found in directory!")
    exit()

print(f"Found {num_images} images to process.")

# -------------------------------------------------------------------------
# 2. تحديد الأبعاد والتنسيق العمودي (3 أعمدة × 4 صفوف)
# -------------------------------------------------------------------------
cols = 3
rows = math.ceil(num_images / cols)

first_img = Image.open(image_files[0])
img_w, img_h = first_img.size

padding = 20
top_margin = 150  # مساحة للعنوان الموسع
bottom_margin = 130  # مساحة للـ Colorbar الموحد بالأسفل

canvas_width = cols * img_w + (cols + 1) * padding
canvas_height = top_margin + rows * img_h + (rows + 1) * padding + bottom_margin

canvas = Image.new("RGB", (canvas_width, canvas_height), color=(255, 255, 255))
draw = ImageDraw.Draw(canvas)

# تحميل الخطوط
try:
    title_font = ImageFont.truetype("arial.ttf", 80)
    sub_font = ImageFont.truetype("arial.ttf", 55)
    cbar_font = ImageFont.truetype("arial.ttf", 35)
except IOError:
    title_font = ImageFont.load_default()
    sub_font = ImageFont.load_default()
    cbar_font = ImageFont.load_default()

# -------------------------------------------------------------------------
# 3. رسم العنوان الرئيسي والوصفي
# -------------------------------------------------------------------------
main_title = "SYNOPTIC EVOLUTION OF SAHARAN CYCLONE & DUST TRANSPORT"
sub_title = (
    "Continuous 12-Hour Evolution (11–16 Mar 2026)  |Black Contours: Mean Sea Level Pressure (hPa)  |  Shaded Regions:"
    " Dust Concentration (mg/kg)"
    )


draw.text(
    (canvas_width // 2, 45),
    main_title,
    fill=(15, 25, 45),
    font=title_font,
    anchor="mm",
)
draw.text(
    (canvas_width // 2, 100),
    sub_title,
    fill=(60, 70, 85),
    font=sub_font,
    anchor="mm",
)

# -------------------------------------------------------------------------
# 4. رص الخرائط داخل الشبكة العمودية (3 × 4)
# -------------------------------------------------------------------------
for idx, img_path in enumerate(image_files):
    r = idx // cols
    c = idx % cols

    x_pos = padding + c * (img_w + padding)
    y_pos = top_margin + padding + r * (img_h + padding)

    img = Image.open(img_path)
    canvas.paste(img, (x_pos, y_pos))
    # رسم البرواز الأسود حول كل خريطة
    draw.rectangle([x_pos, y_pos, x_pos + img_w, y_pos + img_h], outline="black", width=2)
    print(f"Pasted [{idx+1}/{num_images}]: {os.path.basename(img_path)}")

# -------------------------------------------------------------------------
# 5. رسم الـ Colorbar الموحد بأسفل اللوحة
# -------------------------------------------------------------------------
cmap_colors = ["#ffffff", "#fdb837", "#e66101", "#d7191c", "#990000", "#500000"]
labels = ["0.0", "0.5", "1.5", "2.5", "3.5", "4.5", "5.5+"]

cbar_w = int(canvas_width * 0.7)
cbar_h = 50
cbar_x = (canvas_width - cbar_w) // 2
cbar_y = canvas_height - bottom_margin + 30

box_w = cbar_w / len(cmap_colors)

# رسم صناديق الألوان
for i, color in enumerate(cmap_colors):
    bx1 = cbar_x + i * box_w
    by1 = cbar_y
    bx2 = bx1 + box_w
    by2 = cbar_y + cbar_h
    draw.rectangle([bx1, by1, bx2, by2], fill=color, outline="black", width=1)

    # إضافة الأرقام والحدود
    draw.text(
        (bx1, by2 + 8), labels[i], fill="black", font=cbar_font, anchor="mt"
    )
draw.text(
    (cbar_x + cbar_w, cbar_y + cbar_h + 8),
    labels[-1],
    fill="black",
    font=cbar_font,
    anchor="mt",
)
# -------------------------------------------------------------------------
# 6. حفظ اللوحة النهائية عالية الدقة
# -------------------------------------------------------------------------
canvas.save(output_filename, dpi=(300, 300), quality=95)
print(f"\nSUCCESS! High-Resolution Vertical Panel Saved: {os.path.abspath(output_filename)}")