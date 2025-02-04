from PIL import Image, ImageSequence

def clear_gif_background(input_path, output_path, background_color=(255, 255, 255, 0), colors_to_clear=[(255, 255, 255)], tolerance=30):
    # 打开GIF图像
    gif = Image.open(input_path)
    
    # 获取GIF的尺寸
    width, height = gif.size
    
    # 创建一个新的图像列表，用于存储处理后的帧
    frames = []

    # 遍历GIF的每一帧
    for frame in ImageSequence.Iterator(gif):
        # 创建一个新的空白图像，背景为透明
        new_frame = Image.new("RGBA", (width, height), background_color)
        
        # 将帧转换为RGBA模式
        frame = frame.convert("RGBA")
        
        # 获取帧的像素数据
        datas = frame.getdata()
        
        # 创建一个新的像素数据列表，用于存储处理后的像素
        new_data = []
        
        for item in datas:
            # 检查像素是否为需要清除的颜色
            if any(all(abs(item[i] - color[i]) <= tolerance for i in range(3)) for color in colors_to_clear):
                # 将需要清除的颜色替换为透明
                new_data.append(background_color)
            else:
                new_data.append(item)
        
        # 更新帧的像素数据
        frame.putdata(new_data)
        
        # 将处理后的帧绘制到新的空白图像上
        new_frame.paste(frame, (0, 0), frame)
        
        # 将处理后的帧添加到帧列表中
        frames.append(new_frame)
    
    # 保存处理后的GIF图像
    frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, disposal=2)

# 示例用法
input_path = "C:/Users/OneHundred/Desktop/sss/settings.gif"
output_path = "C:/Users/OneHundred/Desktop/sss/settings1.gif"
colors_to_clear = [(255, 255, 255), (0, 0, 0)]  # 需要清除的颜色列表
tolerance = 30  # 容差范围
clear_gif_background(input_path, output_path, colors_to_clear=colors_to_clear, tolerance=tolerance)