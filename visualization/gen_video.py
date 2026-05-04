import cv2
import os

import imageio as iio
from PIL import Image
import numpy as np

from tqdm import tqdm

def video_trans_size(input_mp4, output_h264):
    cap = cv2.VideoCapture(input_mp4)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(width,height)
    
    # 定义编解码器并创建VideoWriter对象
    out = iio.get_writer(output_h264, format='ffmpeg', mode='I', fps=5, codec='libx264', pixelformat='yuv420p', macro_block_size=None)
    while(True):
        ret, frame = cap.read()
        if ret is True:
            
            image = frame[:, :, (2, 1, 0)]
            # 写翻转的框架
            # out.write(frame)
            out.append_data(image)
            # cv.imshow('frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        else:
            break
    # 完成工作后释放所有内容
    cap.release()
    out.close()
    cv2.destroyAllWindows()
    os.remove(input_mp4)


def concat_video(output_path,resize_factor, dir_name):
    # 图片序列的文件夹路径
    if os.path.isdir(dir_name + '/ego_vehicle_0'):
        folder_b = dir_name + '/ego_vehicle_0'
        folder_a = dir_name + '/ego_vehicle_1'
    elif os.path.isdir(dir_name + '/rgb_0'):
        folder_b = dir_name + '/rgb_0'
        folder_a = dir_name + '/rgb_1'
    elif os.path.isdir(dir_name + '/meta_0'):
        folder_b = dir_name + '/meta_0'
        folder_a = dir_name + '/meta_1'
    else:
        print("No such folder")
        return
    # 读取图片文件
    files_a = sorted([os.path.join(folder_a, file) for file in os.listdir(folder_a) if file.endswith('.jpg') or file.endswith('.png')])
    files_b = sorted([os.path.join(folder_b, file) for file in os.listdir(folder_b) if file.endswith('.jpg') or file.endswith('.png')])

    # 确保两个序列长度相同
    # assert len(files_a) == len(files_b), "The sequences do not have the same number of images."

    len_max = max(len(files_a),len(files_b))
    while len(files_a) < len_max:
        files_a.append(files_a[-1])
    while len(files_b) < len_max:
        files_b.append(files_b[-1])
    # files_a = files_a[:len_min]
    # files_b = files_b[:len_min]

    # resize_factor = 2

    # 读取第一张图片来获取尺寸信息
    img_a = cv2.imread(files_a[0])
    height, width, layers = img_a.shape
    height = height // resize_factor
    width = width // resize_factor
    img_size = (width,height)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 定义编解码器
    video = cv2.VideoWriter(output_path, fourcc, 5, (width, height * 2))

    frame = 0
    # 合并图像并添加到视频
    for img_path_a, img_path_b in tqdm(zip(files_a, files_b)):
        frame += 1
        # if frame<16:
        #     continue
        img_a = cv2.imread(img_path_a)
        img_b = cv2.imread(img_path_b)
        
        img_a = cv2.resize(img_a,img_size)
        img_b = cv2.resize(img_b,img_size)

        # 合并图像
        combined_img = cv2.vconcat([img_a, img_b])
        
        # 写入视频
        video.write(combined_img)

    video.release()

if __name__ == '__main__':
    dir_name = "/GPFS/data/changxingliu/V2Xverse/results/results_driving_intersection_internvl_8b_intention_speed_level_5_comm/image/v2x_final/town06_short_r1_ins_sr/town06_short_r1_ins_sr_0_10_17_03_29_06"
    concat_video(dir_name + '/output.mp4', 2, dir_name)
    video_trans_size(dir_name + '/output.mp4',
                    dir_name + '/output_h264.mp4')