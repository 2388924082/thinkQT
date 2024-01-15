# -*- coding: utf-8 -*-
import numpy as np
from skimage import color

MAT_RGB2XYZ = np.array([[0.412453, 0.357580, 0.180423],
                        [0.212671, 0.715160, 0.072169],
                        [0.019334, 0.119193, 0.950227]])

MAT_XYZ2RGB = np.linalg.inv(MAT_RGB2XYZ)

XYZ_REF_WHITE = np.array([0.95047, 1.0, 1.08883])


def rgb_to_lab(rgb):
    """
    Convert color space from rgb to lab

    Parameters:
    -----------
    rgb: numpy array, dtype = uint8
        3-dim array, shape is [H, W, C], C must be 3

    Returns:
    --------
    numpy array in lab color space, dtype = float
    """
    return xyz_to_lab(rgb_to_xyz(rgb))


def lab_to_rgb(lab):
    """
    Convert color space from lab to rgb

    Parameters:
    -----------
    lab: numpy array, dtype = float
        3-dim array, shape is [H, W, C], C must be 3

    Returns:
    --------
    numpy array in rgb color space, dtype = uint8
    """
    return xyz_to_rgb(lab_to_xyz(lab))


def rgb_to_xyz(rgb):
    """
    Convert color space from rgb to xyz

    Parameters:
    -----------
    rgb: numpy array, dtype = uint8
        3-dim array, shape is [H, W, C], C must be 3

    Returns:
    --------
    xyz: numpy array, dtype = float
        array in xyz color space
    """
    # convert dtype from uint8 to float
    xyz = rgb.astype(np.float64) / 255.0

    # gamma correction
    mask = xyz > 0.04045
    xyz[mask] = np.power((xyz[mask] + 0.055) / 1.055, 2.4)
    xyz[~mask] /= 12.92

    # linear transform
    xyz = xyz @ MAT_RGB2XYZ.T
    return xyz


def xyz_to_rgb(xyz):
    """
    Convert color space from xyz to rgb

    Parameters:
    -----------
    xyz: numpy array, dtype = float
        3-dim array, shape is [H, W, C], C must be 3

    Returns:
    --------
    rgb: numpy array, dtype = uint8
        array in rgb color space
    """
    # linear transform
    rgb = xyz @ MAT_XYZ2RGB.T

    # gamma correction
    mask = rgb > 0.0031308
    rgb[mask] = 1.055 * np.power(rgb[mask], 1.0 / 2.4) - 0.055
    rgb[~mask] *= 12.92

    # clip and convert dtype from float to uint8
    rgb = np.round(255.0 * np.clip(rgb, 0, 1)).astype(np.uint8)
    return rgb


def xyz_to_lab(xyz):
    """
    Convert color space from xyz to lab

    Parameters:
    -----------
    xyz: numpy array, dtype = float
        3-dim array, shape is [H, W, C], C must be 3

    Returns:
    --------
    lab: numpy array, dtype = float
        array in lab color space
    """
    # normalization
    xyz /= XYZ_REF_WHITE

    # nonlinear transform
    mask = xyz > 0.008856
    xyz[mask] = np.power(xyz[mask], 1.0 / 3.0)
    xyz[~mask] = 7.787 * xyz[~mask] + 16.0 / 116.0
    x, y, z = xyz[..., 0], xyz[..., 1], xyz[..., 2]

    # linear transform
    lab = np.empty(xyz.shape)
    lab[..., 0] = (116.0 * y) - 16.0  # L channel
    lab[..., 1] = 500.0 * (x - y)  # a channel
    lab[..., 2] = 200.0 * (y - z)  # b channel
    return lab


def lab_to_xyz(lab):
    """
    Convert color space from lab to xyz

    Parameters:
    -----------
    lab: numpy array, dtype = float
        3-dim array, shape is [H, W, C], C must be 3

    Returns:
    --------
    xyz: numpy array, dtype = float
        array in xyz color space
    """
    # linear transform
    l, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    xyz = np.empty(lab.shape)
    xyz[..., 1] = (l + 16.0) / 116.0
    xyz[..., 0] = a / 500.0 + xyz[..., 1]
    xyz[..., 2] = xyz[..., 1] - b / 200.0
    index = xyz[..., 2] < 0
    xyz[index, 2] = 0

    # nonlinear transform
    mask = xyz > 0.2068966
    xyz[mask] = np.power(xyz[mask], 3.0)
    xyz[~mask] = (xyz[~mask] - 16.0 / 116.0) / 7.787

    # de-normalization
    xyz *= XYZ_REF_WHITE
    return xyz


# 生成lab坐标的背景图
def range_to_lab(l=75, xrange=(-128, 128, 1), yrange=(128, -128, -1)):
    arr = []
    for b in np.arange(yrange[0], yrange[1], yrange[2]):
        temp = []
        for a in np.arange(xrange[0], xrange[1], xrange[2]):
            temp.append([l, a, b])
        arr.append(temp)
    arr = np.array(arr, dtype=np.int16)
    return arr


def range_to_lab_img(l=75, xrange=(-128, 128, 1), yrange=(128, -128, -1)):
    lab = range_to_lab(l, xrange, yrange)
    rgb_img = lab_to_rgb(lab)
    return rgb_img


rgbList_standard = np.array(
    [[116, 79, 63], [197, 151, 130], [94, 123, 157], [87, 107, 63], [133, 131, 178], [102, 190, 170],
     [218, 123, 42], [74, 92, 165], [197, 85, 98], [92, 59, 107], [159, 188, 62], [230, 163, 46],
     [46, 62, 151], [69, 150, 70], [178, 47, 58], [238, 200, 26], [189, 84, 148], [0, 137, 167],
     [242, 242, 242], [201, 201, 201], [161, 161, 161], [124, 124, 124], [85, 86, 87], [51, 51, 53]])
labList_standard = rgb_to_lab(rgbList_standard)
if __name__ == '__main__':

    def te_lab_img():
        np.set_printoptions(threshold=np.inf)
        import matplotlib.pyplot as plt
        # 图像范围0-255
        l = 75
        arange = [-128, 128, 1]
        brange = [128, -128, -1]
        lab_img = range_to_lab_img(l, arange, brange)
        plt.imshow(lab_img)
        plt.imsave('lab_img.png', lab_img)
        plt.show()
    te_lab_img()

    def te_with_skimage():
        rgb = np.array([[[194, 150, 130]]], dtype=np.uint8)
        xyz = rgb_to_xyz(rgb)
        lab = xyz_to_lab(xyz)
        xyz_ = lab_to_xyz(lab)
        rgb_ = xyz_to_rgb(xyz_)

        print('-' * 15, ' self defined function result ', '-' * 15)
        print('rgb:', rgb)
        print('xyz:', xyz)
        print('lab:', lab)
        print('xyz_inverse:', xyz_)
        print('rgb_inverse:', rgb_)

        xyz2 = color.rgb2xyz(rgb)
        lab2 = color.xyz2lab(xyz2)
        xyz2_ = color.lab2xyz(lab2)
        rgb2_ = color.xyz2rgb(xyz2_)
        rgb2_ = np.round(255.0 * np.clip(rgb2_, 0, 1)).astype(np.uint8)

        print('-' * 15, ' skimage result ', '-' * 15)
        print('rgb:', rgb)
        print('xyz:', xyz2)
        print('lab:', lab2)
        print('xyz_inverse:', xyz2_)
        print('rgb_inverse:', rgb2_)


    def te_24colors():
        # 24色卡转换
        np.set_printoptions(suppress=True)
        rgbList = np.array(
            [[[116, 79, 63], [197, 151, 130], [94, 123, 157], [87, 107, 63], [133, 131, 178], [102, 190, 170],
              [218, 123, 42], [74, 92, 165], [197, 85, 98], [92, 59, 107], [159, 188, 62], [230, 163, 46],
              [46, 62, 151], [69, 150, 70], [178, 47, 58], [238, 200, 26], [189, 84, 148], [0, 137, 167],
              [242, 242, 242], [201, 201, 201], [161, 161, 161], [124, 124, 124], [85, 86, 87], [51, 51, 53]]])
        labList = rgb_to_lab(rgbList)
        rgbList_inserve = lab_to_rgb(labList)
        print('rgbList:', rgbList)
        print('24色卡LAB:', labList)
        print('rgbList_inserve:', rgbList_inserve)

    # te_24colors()
    # te_with_skimage()
