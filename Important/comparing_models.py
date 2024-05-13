"""
# Comparing Models

---------------------------------------------------------------------------------------------------------------------------------

Kye Emond

Janurary 10, 2024

---------------------------------------------------------------------------------------------------------------------------------

A script you can run to plot the confidence intervals generated by any set of models stored in a directory
"""

# Imports
import numpy as np
import numpy.polynomial.polynomial as npp
import glob as glob
import pickle as pkl
import scipy.optimize as spo
import scipy.stats.distributions as spsd
import keras.models as km
import matplotlib.pyplot as plt
import typing as ty
import numpy.typing as npt
import matplotlib.pyplot as plt

# Main function
def main() -> None:
    
    print("\n" + "START".center(50, "-"))
    
    # Loading data
    P_VALUE = 0.95
    C = 1.0
    TEST_DATA_PATH = f"/home/kye/TestingModels/FakeData/fake_data_cHW={C}.pkl"
    TEST_WEIGHTS_PATH = f"/home/kye/TestingModels/FakeData/fake_weights_cHW={C}.pkl"
    MODEL_DIRECTORY = "/home/kye/Results/OldLong2"
    TOTAL_DATA_PATH = "/home/kye/Data/training_cHW_events.pkl"
    NAME = f"/home/kye/2old100x10_cHW={C}_"
    XLABEL = r"$c_\mathrm{HW}$ Value"
    EXTRA_PLOT_WIDTH = 0.01#0.003
    PLOT_SHRINK = 1.0
    
    print("\n" + "LOADING DATA".center(50, "-"))
    
    # Get the function that can output number of events
    total_num_estimate = build_total_num_estimate(datapath=TOTAL_DATA_PATH)
    print(type(total_num_estimate))
    print(total_num_estimate(C))
    
    # Load and format the test data
    with open(TEST_DATA_PATH, "rb") as datafile:
        data = pkl.load(datafile)
    kinematics = data.to_numpy()[:, 1:]
    multiples = data.to_numpy()[:, 0]
    # Load and format the test weights
    with open(TEST_WEIGHTS_PATH, "rb") as datafile:
        weights = pkl.load(datafile)
    
    print("\n" + "SEARCHING FOR MODELS".center(50, "-"))
    
    # Load all the model paths from the directory into a dictionary
    files = glob.glob(MODEL_DIRECTORY + "/*/")
    titles = [list(filter(lambda item: item != "", file.split("/")))[-1] for file in files]
    
    print("\n" + "EVALUATING PERFORMANCES".center(50, "-"))
    
    # Iteratively evaluate each model on the test data and store some plots
    for file, title in list(zip(files, titles))[0:1]:
        # try:
        print("\n" + f"STARTING {title}".center(50, "-"))
        
        # Get the paths to the alpha and beta models
        alpha_path = next(filter(lambda name: "alpha" in name, glob.glob(file + "/*/")), None)
        beta_path = next(filter(lambda name: "beta" in name, glob.glob(file + "/*/")), None)
        
        print("\n" + "LOADING MODELS".center(50, "-"))
        
        # Load the submodels
        alpha = km.load_model(alpha_path, compile=False)
        beta = km.load_model(beta_path, compile=False)
        
        # Design the ratio estimate function
        def ratio_estimate(kinematics: npt.ArrayLike, coefficient: float) -> np.ndarray:
            """Calculate the estimate for the differential cross-section ratio of a set of events at a given Wilson Coefficient. 

            Args:
                kinematics (npt.ArrayLike): A 2D array storing kinematic variables along axis 1 and individual events along\
                    axis 0. 
                coefficient (float): The Wilson Coefficient value at which to evaluate the ratio estimate. 

            Returns:
                np.ndarray: A 1D array of the ratio estimates for each event. 
            """
            return (1.0 + coefficient * alpha(kinematics)[..., 0]) ** 2.0 + (coefficient * beta(kinematics)[..., 0]) ** 2.0
        
        def llr_estimate(kinematics: npt.ArrayLike, coefficient: float) -> float:
            """Calculate the log-likelihood ratio for a set of kinematics and a given coefficient. 

            Args:
                kinematics (npt.ArrayLike): A 2D array storing kinematic variables along axis 1 and individual events along\
                    axis 0. 
                coefficient (float): The Wilson Coefficient value at which to evaluate the ratio estimate. 

            Returns:
                float: The log-likelihood ratio estimate for the coefficient given the data. 
            """
            
            return (total_num_estimate(coefficient=coefficient) - total_num_estimate(coefficient=0.0) 
                    - np.sum(multiples * np.log(ratio_estimate(kinematics=kinematics, coefficient=coefficient))))
        
        
        # Interval plotting code
        # Get alpha value
        cutoff = spsd.chi2.ppf(P_VALUE, df=1)
        print(f"cutoff value is {cutoff}")
        
        # Get the maximum log likelihood ratio
        opt = spo.minimize_scalar(lambda x: llr_estimate(kinematics=kinematics, coefficient=x), 
                                    bracket=(-10.0, 10.0),
                                    tol=1e-6)
        print(f"minimum found at {opt.x}")
        min_val = opt.fun
        
        # Define the test statistic with it
        def test_stat(kinematics: npt.ArrayLike, coefficient: float) -> float:
            return -2.0 * (min_val - llr_estimate(kinematics=kinematics, coefficient=coefficient))
        
        # Find confidence intervals
        left_root = spo.fsolve(lambda c: test_stat(kinematics=kinematics, coefficient=c) - cutoff, opt.x - 0.01, xtol=1e-6)
        right_root = spo.fsolve(lambda c: test_stat(kinematics=kinematics, coefficient=c) - cutoff, opt.x + 0.01, xtol=1e-6)
        
        print("[", left_root, ",", right_root, "]")
        
        # Plotting Intervals
        plt.clf()
        c_tests = np.linspace(left_root - EXTRA_PLOT_WIDTH, right_root + EXTRA_PLOT_WIDTH, 50)
        test_stat_estimate_values = np.array([test_stat(kinematics=kinematics, coefficient=c) for c in c_tests])
        plt.axhline(cutoff, ls=":", label=r"$\alpha$", lw=3 * PLOT_SHRINK)
        plt.plot(c_tests, test_stat_estimate_values, label=r"$\hat \Lambda$", lw=2 * PLOT_SHRINK)
        plt.axvspan(np.squeeze(left_root), np.squeeze(right_root), ec="salmon", fc=("salmon", 0.4), label="95% Confidence Interval")
        plt.axvline(left_root, color="salmon", lw=2 * PLOT_SHRINK)
        plt.axvline(right_root, color="salmon", lw=2 * PLOT_SHRINK)
        plt.axvline(C, color="green", lw=2 * PLOT_SHRINK, ls=":")
        plt.xlabel(XLABEL, fontsize=15 * PLOT_SHRINK)
        plt.ylabel(r"$\hat \Lambda$ Value", fontsize=15 * PLOT_SHRINK)
        plt.xticks(plt.gca().get_xticks()[slice(1, None, round(PLOT_SHRINK))], fontsize=12 * PLOT_SHRINK)
        plt.yticks(plt.gca().get_yticks()[slice(1, None, round(PLOT_SHRINK))], fontsize=12 * PLOT_SHRINK)
        plt.savefig(NAME + str(title) + ".pdf", bbox_inches="tight", facecolor=(1, 1, 1, 1))


def build_total_num_estimate(datapath: str) -> ty.Callable[[npt.ArrayLike], np.ndarray]:
    """Return a function that outputs the expected number of events for each Wilson Coefficient. 

    Args:
        datapath (str): The path to a representative datafile. 

    Returns:
        ty.Callable: the function TODO
    """
    
    with open(datapath, "rb") as datafile:
        data = pkl.load(datafile)
        
        weight_columns = list(filter(lambda name: "weight_" in name, data.columns))
        data = data[weight_columns].sum(axis=0).to_numpy()
        x_values = [string_to_float(name) if name != "weight_sm" else 0.0 for name in weight_columns]
        
        coefs = npp.polyfit(x_values, data, 2)
    
    def total_num_estimate(coefficient: npt.ArrayLike) -> np.ndarray:
        return npp.polyval(coefficient, coefs)
    
    return total_num_estimate
        
    
    
def string_to_float(string: str) -> float:
    """Return the float corresponding to the weird nTuple-formatted string.

    Args:
        string (str): The formatted string to convert.

    Returns:
        float: The float version of the string
    """
    
    number_bit = string.split("_")[-1].replace("pos", "").replace("neg", "-").replace("p", ".")
    return float(number_bit)

# Call the main function
if __name__ == "__main__":
    main()
