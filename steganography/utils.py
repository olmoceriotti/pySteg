from skimage import img_as_float, img_as_ubyte
import numpy as np

def difference(original, new):
    dif = abs(img_as_float(original) - img_as_float(new))
    black = original[:,:,0] * 0
    dif_r = dif[:, :, 0]
    dif_g = dif[:, :, 1]
    dif_b = dif[:, :, 2]
    dif = np.dstack((dif_b, dif_g, dif_r))
    dif -= dif.min()
    dif = dif * 1 / dif.max()

    dif_r -= dif_r.min()
    dif_r = dif_r / dif_r.max()
    dif_r = np.dstack((dif_r, black, black))

    dif_g -= dif_g.min()
    dif_g = dif_g / dif_g.max()
    dif_g = np.dstack((black, dif_g, black))

    dif_b -= dif_b.min()
    dif_b = dif_b / dif_b.max()
    dif_b = np.dstack((black, black, dif_b))

    return[
        ("difference.png", img_as_ubyte(dif)),
        ("difference_r.png", img_as_ubyte(dif_r)),
        ("difference_g.png", img_as_ubyte(dif_g)),
        ("difference_b.png", img_as_ubyte(dif_b))
        ]