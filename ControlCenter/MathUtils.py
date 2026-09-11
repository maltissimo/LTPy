import numpy as np
from jedi.inference.recursion import total_function_execution_limit
from scipy.ndimage import center_of_mass
from numba import njit


def um2mm( umvalue):
    # converts microns to mm
    return (umvalue / 1000)


def mm2um(mmvalue):
    # converts mm to microns
    return (mmvalue * 1000)


@njit
def fwhm( nparray):
    """
    Returns the FWHM of a 1D array. If a peak is defined in X-y Coordinates, then
    finds the right and left most indexes of the half max of hte peak,
    then compute the nparrayX full width from those indexes
    The return value is in the units of nparrayX.
    """

    halfmax = np.max(nparray) / 2  # this finds the halfmax  of the array
    above_half = nparray >= halfmax
    indexes = np.where(above_half)[0]
    FWHM = indexes[-1] - indexes[0]
    """d = np.sign(halfmax - nparrayY[0:-1]) - np.sign(halfmax - nparrayY[1:])
    # find the right and left most indexes:
    left_index = np.where(d > 0)[0]
    right_index = np.where(d < 0)[-1]
    FWHM = nparrayX[right_index] - nparrayX[left_index]"""

    return FWHM

def centroid( ndarray):
    """
    this had to be modified from a simple scipy.center_of_mass, as it doesn't track correctly the spot center, most likely
    because scipy.center_of_mass tracks all the reflections detected by the camera, but we are only intereste in the most
    intense one.

    centroid = center_of_mass(ndarray)
    return(np.array(centroid))

    :param ndarray:
    :return:
    """
    max_index = np.unravel_index(np.argmax(ndarray), ndarray.shape)

    # Original code commented out to fix boundary issues
    # x_min, x_max = int(max_index[0]) - 150, int(max_index[0]) + 150
    # y_min, y_max = int(max_index[1]) - 150, int(max_index[1]) + 150

    # New code with boundary clamping
    h, w = ndarray.shape
    x_min = max(0, int(max_index[0]) - 150)
    x_max = min(h, int(max_index[0]) + 150)
    y_min = max(0, int(max_index[1]) - 150)
    y_max = min(w, int(max_index[1]) + 150)

    roi = ndarray[x_min:x_max, y_min:y_max]
    back_sub = roi - np.min(roi)
    com_roi = (center_of_mass(back_sub)) # center of mass of the ROI
            #print("this is the Center of Mass ROI: ", com_roi)
    com_global = ((com_roi[0]) + x_min, (com_roi[1]) + y_min) # removed the integer casting, as I'm trying sub-pixel resolution.
            #print(com_global[0], com_global[1])

    return (com_global)

def centroid_thresholded(image, roi_radius =  40, threshold_ratio= 0.15):
    """
    Sub-pixel centroiding using a symmetric ROI and thresholded center of mass.

    :param image: 2D detector array.
    :param roi_radius: Half-width of the square ROI (pixels). Should be ~3-4x the beam 1/e^2 radius.
    :param threshold_ratio: Relative cutoff (0.0 to 1.0) below which intensity is zeroed.
    :return: (y_centroid, x_centroid) in global sensor coordinates (row, col).
    """
    # 1. Peak location
    row_peak, col_peak = np.unravel_index(np.argmax(image), image.shape)

    # 2. Extract symmetric ROI with padding to prevent boundary truncation artifacts
    r_min = row_peak - roi_radius
    r_max = row_peak + roi_radius + 1
    c_min = col_peak - roi_radius
    c_max = col_peak + roi_radius + 1

    pad_top = max(0, -r_min)
    pad_bottom = max(0, r_max - image.shape[0])
    pad_left = max(0, -c_min)
    pad_right = max(0, c_max - image.shape[1])

    # Crop valid sensor area
    valid_r_min = max(0, r_min)
    valid_r_max = min(image.shape[0], r_max)
    valid_c_min = max(0, c_min)
    valid_c_max = min(image.shape[1], c_max)

    roi = image[valid_r_min:valid_r_max, valid_c_min:valid_c_max].astype(np.float64)

    # Pad with constant estimated background if the window intersects detector edges
    if any((pad_top, pad_bottom, pad_left, pad_right)):
        bg_val = np.median(roi)
        roi = np.pad(roi, ((pad_top, pad_bottom), (pad_left, pad_right)), mode='constant', constant_values=bg_val)

    # 3. Background subtraction & thresholding
    # Estimate local background from ROI periphery
    border = np.concatenate([roi[0, :], roi[-1, :], roi[:, 0], roi[:, -1]])
    local_bg = np.median(border)
    roi_sub = roi - local_bg
    roi_sub[roi_sub < 0] = 0.0

    peak_val = np.max(roi_sub)
    if peak_val <= 0:
        return float(row_peak), float(col_peak)

    # Zero-out pixels below threshold ratio
    cutoff = threshold_ratio * peak_val
    roi_sub[roi_sub < cutoff] = 0.0

    # 4. First moment on thresholded signal
    total_mass = np.sum(roi_sub)
    if total_mass == 0:
        return float(row_peak), float(col_peak)

    # Grid relative to the padded window
    grid_r, grid_c = np.indices(roi_sub.shape)
    com_r = np.sum(grid_r * roi_sub) / total_mass
    com_c = np.sum(grid_c * roi_sub) / total_mass

    # Global coordinates: unpad and offset
    global_r = com_r - pad_top + r_min
    global_c = com_c - pad_left + c_min

    return (float(global_r), float(global_c))

def compute_ltp_centroid(image, roi_half_width=150, soft_power=1.15):
    """
    Drop-in replacement that preserves true 2D center-of-mass weighting
    while fixing background offset and edge clamping artifacts.
    """
    img = image.astype(np.float64)
    h, w = img.shape

    # 1. Peak location
    r_peak, c_peak = np.unravel_index(np.argmax(img), (h, w))

    # 2. Extract symmetric ROI without asymmetric shape changes
    r_min = r_peak - roi_half_width
    r_max = r_peak + roi_half_width + 1
    c_min = c_peak - roi_half_width
    c_max = c_peak + roi_half_width + 1

    # Bounds clipping
    r_min_clamped = max(0, r_min)
    r_max_clamped = min(h, r_max)
    c_min_clamped = max(0, c_min)
    c_max_clamped = min(w, c_max)

    roi = img[r_min_clamped:r_max_clamped, c_min_clamped:c_max_clamped]

    # 3. Robust background subtraction via border median
    # (np.min leaves positive noise bias; median removes true baseline)
    border = np.concatenate([roi[0, :], roi[-1, :], roi[:, 0], roi[:, -1]])
    bg = np.median(border)
    roi_sub = np.maximum(roi - bg, 0.0)

    # 4. Soft weighting instead of hard thresholding
    # soft_power=1.0 is pure standard 2D center_of_mass
    # soft_power=1.5 or 2.0 gently supresses baseline tails without digital step noise
    if soft_power != 1.0:
        roi_sub = roi_sub ** soft_power

    # 5. True 2D center of mass
    com_local = center_of_mass(roi_sub)

    # Fallback if ROI is completely dark
    if np.isnan(com_local[0]) or np.isnan(com_local[1]):
        return np.array([float(r_peak), float(c_peak)])

    global_r = com_local[0] + r_min_clamped
    global_c = com_local[1] + c_min_clamped

    return np.array([global_r, global_c])

def splitimage( nparray2D):
    """"
    This is used to provide arrays of a laser image (i.e. a spot).
    First, it finds the centroid of the spot, which provides X and Y pixel indexes of where the
    centroid of the image can be found.
    Then it splits the 2D array along those coordinates, returning 2, 1D vectors

    """
    center = centroid(nparray2D)
    centerX, centerY = np.round(center).astype(int)
    #print(centerX, centerY)

    X_vector = nparray2D[centerX, :]
    Y_vector = nparray2D[:, centerY]

    return (X_vector, Y_vector)


def calc_2D_fwhm(nparray2D):
    HOR_vector, VER_vector = splitimage(nparray2D)
    """HOR_axis = np.arange(0, len(HOR_vector), 1)
    VER_axis = np.arange(0, len(VER_vector), 1)"""

    HOR_FWHM = fwhm(HOR_vector)
    VER_FWHM = fwhm(VER_vector)

    return (HOR_FWHM, VER_FWHM)


def my_fit(arrayX, arrayY, order):
    """
    :param arrayX: typically, an array with the step positions of the measurement
    :param arrayY: array of values to be fit
    :param order: order of the polynomial fit
    :return: an array of fitted data and the radius of the sphere as the 0-th order coefficient of the fit
    """

    coeff = np.polyfit(arrayX, arrayY, order)
    p = np.poly1d(coeff)
    fit = p(arrayX)
    radius = 1 / coeff[0]
    #print("Radius as coeff[0], in m: ", radius/1000000)
    return (fit, radius)

def gaussian_filter ( residual_slope_array,
                    beam_step=None,
                    beam_waist=None):

    """"
    This method takes the residual slope array, and gaussian-smoothes it due to beam big size/
    The math is as follows:
    fitted_slope, radius_of_curvature =  my_fit(arrayX, arrayY, order)
    residual_slope = measured_slope - fitted_slope
    then the Gaussian filter is applied to the residual to deconvolve the laser spot size at the mirror:
    smoothed_slope = gaussian_filter(residual_slope).

    """
    from scipy.ndimage import gaussian_filter1d

    if beam_step is None:
        beam_step = self.stepsize  # this is in mm
    if beam_waist is None:
        beam_waist = 2.2  # FHWM I know in px time px size
    sigma_points = (beam_waist / 2.355) / beam_step
    smoothed_slope = gaussian_filter1d(residual_slope_array,
                                       sigma=sigma_points,
                                       mode='reflect')
    return (smoothed_slope)

def RMS(array):
    """
    calculates the root mean square value of any array
    :param array: input array for which the RMS calculation is needed
    :return: an RMS value, same units as array.
    """
    """mysum = np.sum(array)
    nr_of_points = len(array)"""
    RMS = np.sqrt(np.mean(array**2))
    return (RMS)


def is_float(string):
    try:
        float(string)
        return True
    except (ValueError):
        return False


def compare_within(number1, number2, tolerance):
    """Function to compare two numbers withtin a tolerance"""
    if abs(number1 - number2) < tolerance:
        return True
    else:
        return False

def mult_check(size, base):
    """
    This function checks if size is an even integer multiple of base. It returns that multiple.
    If size//base is NOT an even integer multiple, it rounds the result to the next even value.
    Used in Detector.py to set ROI, as the Basler camera is picky about values of Cols and rows

    :param size: desired size of the ROI in px
    :param base: Basler camera value, 48 for width and 4 for height.
    :return: check the value then used to set the ROI.
    """
    check = size//base

    if check % 2 != 0:
        check +=1
    return(check)