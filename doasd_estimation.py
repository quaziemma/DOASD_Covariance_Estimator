# -*- coding: utf-8 -*-
"""DOASD_Estimation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/maofosu1/DOASD/blob/main/DOASD_Estimation.ipynb
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

"""
=======================================================================
Shrinkage covariance estimation: LedoitWolf vs OAS vs OASD and max-likelihood
=======================================================================

When working with covariance estimation, the usual approach is to use
a maximum likelihood estimator, such as the
:class:`sklearn.covariance.EmpiricalCovariance`. It is unbiased, i.e. it
converges to the true (population) covariance when given many
observations. However, it can also be beneficial to regularize it, in
order to reduce its variance; this, in turn, introduces some bias. This
example illustrates the simple regularization used in
`shrunk_covariance` estimators. In particular, it focuses on how to
set the amount of regularization, i.e. how to choose the bias-variance
trade-off.

Here we compare 3 approaches:

* Setting the parameter by cross-validating the likelihood on three folds
  according to a grid of potential shrinkage parameters.

* A close formula proposed by Ledoit and Wolf to compute
  the asymptotically optimal regularization parameter (minimizing a MSE
  criterion), yielding the :class:`sklearn.covariance.LedoitWolf`
  covariance estimate.

* An improvement of the Ledoit-Wolf shrinkage, the
  :class:`sklearn.covariance.OAS`, proposed by Chen et al. Its
  convergence is significantly better under the assumption that the data
  are Gaussian, in particular for small samples.

To quantify estimation error, we plot the likelihood of unseen data for
different values of the shrinkage parameter. We also show the choices by
cross-validation, or with the LedoitWolf and OAS estimates.

Note that the maximum likelihood estimate corresponds to no shrinkage,
and thus performs poorly. The Ledoit-Wolf estimate performs really well,
as it is close to the optimal and is computational not costly. In this
example, the OAS estimate is a bit further away. Interestingly, both
approaches outperform cross-validation, which is significantly most
computationally costly.


"""

print(__doc__)

import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg

from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance, \
    log_likelihood, empirical_covariance
from sklearn.model_selection import GridSearchCV


# #############################################################################
# Generate sample data
n_features, n_samples = 40, 20
np.random.seed(42)
base_X_train = np.random.normal(size=(n_samples, n_features))
base_X_test = np.random.normal(size=(n_samples, n_features))

# Color samples
coloring_matrix = np.random.normal(size=(n_features, n_features))
X_train = np.dot(base_X_train, coloring_matrix)
X_test = np.dot(base_X_test, coloring_matrix)

# #############################################################################
# Compute the likelihood on test data

# spanning a range of possible shrinkage coefficient values
shrinkages = np.logspace(-2, 0, 30)
negative_logliks = [-ShrunkCovariance(shrinkage=s).fit(X_train).score(X_test)
                    for s in shrinkages]

# under the ground-truth model, which we would not have access to in real
# settings
real_cov = np.dot(coloring_matrix.T, coloring_matrix)
emp_cov = empirical_covariance(X_train)
loglik_real = -log_likelihood(emp_cov, linalg.inv(real_cov))

# #############################################################################
# Compare different approaches to setting the parameter

# GridSearch for an optimal shrinkage coefficient
tuned_parameters = [{'shrinkage': shrinkages}]
cv = GridSearchCV(ShrunkCovariance(), tuned_parameters)
cv.fit(X_train)

# Ledoit-Wolf optimal shrinkage coefficient estimate
lw = LedoitWolf()
loglik_lw = lw.fit(X_train).score(X_test)

# OAS coefficient estimate
oa = OAS()
loglik_oa = oa.fit(X_train).score(X_test)

# #############################################################################
# Plot results
fig = plt.figure()
plt.title("Regularized covariance: likelihood and shrinkage coefficient")
plt.xlabel('Regularization parameter: shrinkage coefficient')
plt.ylabel('Error: negative log-likelihood on test data')
# range shrinkage curve
plt.loglog(shrinkages, negative_logliks, label="Negative log-likelihood")

plt.plot(plt.xlim(), 2 * [loglik_real], '--r',
         label="Real covariance likelihood")

# adjust view
lik_max = np.amax(negative_logliks)
lik_min = np.amin(negative_logliks)
ymin = lik_min - 6. * np.log((plt.ylim()[1] - plt.ylim()[0]))
ymax = lik_max + 10. * np.log(lik_max - lik_min)
xmin = shrinkages[0]
xmax = shrinkages[-1]
# LW likelihood
plt.vlines(lw.shrinkage_, ymin, -loglik_lw, color='magenta',
           linewidth=3, label='Ledoit-Wolf estimate')
# OAS likelihood
plt.vlines(oa.shrinkage_, ymin, -loglik_oa, color='purple',
           linewidth=3, label='OAS estimate')
# best CV estimator likelihood
plt.vlines(cv.best_estimator_.shrinkage, ymin,
           -cv.best_estimator_.score(X_test), color='cyan',
           linewidth=3, label='Cross-validation best estimate')

plt.ylim(ymin, ymax)
plt.xlim(xmin, xmax)
plt.legend()

plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance, empirical_covariance

# Generate sample data
n_features, n_samples = 40, 20
np.random.seed(42)
base_X_train = np.random.normal(size=(n_samples, n_features))
base_X_test = np.random.normal(size=(n_samples, n_features))

# Color samples
coloring_matrix = np.random.normal(size=(n_features, n_features))
X_train = np.dot(base_X_train, coloring_matrix)
X_test = np.dot(base_X_test, coloring_matrix)

# Compute the true covariance
true_cov = np.dot(coloring_matrix.T, coloring_matrix)

# Fit covariance estimators
shrunk_cov = ShrunkCovariance().fit(X_train)
lw = LedoitWolf().fit(X_train)
oa = OAS().fit(X_train)
oasd = ShrunkCovariance(shrinkage=0.5).fit(X_train)  # OASD estimator

# Plot results
plt.figure(figsize=(14, 4))

# Plot true covariance
plt.subplot(1, 4, 1)
plt.imshow(true_cov, cmap='viridis', interpolation='nearest')
plt.title('True Covariance')
plt.colorbar()
print("True Covariance:")
print(true_cov)


# Plot Ledoit-Wolf Covariance
plt.subplot(1, 4, 3)
plt.imshow(lw.covariance_, cmap='viridis', interpolation='nearest')
plt.title('Ledoit-Wolf Covariance')
plt.colorbar()
print("Ledoit-Wolf Covariance:")
print(lw.covariance_)

# Plot OAS Covariance
plt.subplot(1, 4, 4)
plt.imshow(oa.covariance_, cmap='viridis', interpolation='nearest')
plt.title('OAS Covariance')
plt.colorbar()
print("OAS Covariance:")
print(oa.covariance_)

# Plot OASD Covariance
plt.subplot(1, 4, 2)
plt.imshow(oasd.covariance_, cmap='viridis', interpolation='nearest')
plt.title('OASD Covariance')
plt.colorbar()
print("OASD Covariance:")
print(oasd.covariance_)

plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance
from sklearn.metrics import mean_squared_error

# Parameters
n_features = 40  # Number of features
sample_sizes = np.arange(6, 30)  # Sample sizes from 6 to 29

# Define a function to generate sample data with different variable scales
def generate_data(n_samples, n_features):
    base_X_train = np.random.normal(size=(n_samples, n_features))
    scaling_factors = np.arange(1, n_features + 1)
    X_train = base_X_train * scaling_factors
    return X_train

# Define a function to compute RMSE for a given estimator and sample size
def compute_rmse(estimator, X_train):
    true_cov = np.cov(X_train, rowvar=False)
    estimator.fit(X_train)
    estimated_cov = estimator.covariance_
    return np.sqrt(mean_squared_error(true_cov.ravel(), estimated_cov.ravel()))

# Fit covariance estimators for different sample sizes and compute RMSE
rmse_results = {'Ledoit-Wolf': [], 'OAS': [], 'OASD': []}
for n_samples in sample_sizes:
    X_train = generate_data(n_samples, n_features)
    for estimator_name, estimator in [('Ledoit-Wolf', LedoitWolf()),
                                      ('OAS', OAS()),
                                      ('OASD', ShrunkCovariance(shrinkage=0.5))]:
        rmse = compute_rmse(estimator, X_train)
        rmse_results[estimator_name].append(rmse)

# Print RMSE values for each estimator across sample sizes
print("RMSE values:")
for estimator_name, rmse_values in rmse_results.items():
    print(f"{estimator_name}: {rmse_values}")

# Plot RMSE across sample sizes for each estimator
plt.figure(figsize=(10, 6))
for estimator_name, rmse_values in rmse_results.items():
    plt.plot(sample_sizes, rmse_values, label=estimator_name)

plt.title('RMSE of Covariance Estimators Across Sample Sizes')
plt.xlabel('Sample Size')
plt.ylabel('RMSE')
plt.legend()
plt.grid(True)
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import ShrunkCovariance
from sklearn.metrics import mean_squared_error

# Parameters
n_features = 40  # Number of features
sample_size = 100  # Sample size
diag_shrinkage_values = np.linspace(0, 1, 20)  # Diagonal shrinkage values from 0 to 1
off_diag_shrinkage_values = np.linspace(0, 1, 20)  # Off-diagonal shrinkage values from 0 to 1

# Generate sample data
np.random.seed(42)
X_train = np.random.normal(size=(sample_size, n_features))

# True covariance matrix (since we're simulating data, we don't have a true covariance, so we'll use the sample covariance)
true_covariance = np.cov(X_train, rowvar=False)

# Function to compute RMSE for diagonal and off-diagonal shrinkage
def compute_shrinkage_rmse(diag_shrinkage, off_diag_shrinkage):
    # Fit ShrunkCovariance estimator with given shrinkage parameters
    estimator = ShrunkCovariance(shrinkage=diag_shrinkage, assume_centered=True)
    estimator.fit(X_train)

    # Compute estimated covariance matrix
    estimated_covariance = estimator.covariance_

    # Compute RMSE for diagonal and off-diagonal shrinkage
    rmse_diag = np.sqrt(mean_squared_error(np.diag(true_covariance), np.diag(estimated_covariance)))
    rmse_off_diag = np.sqrt(mean_squared_error(true_covariance.ravel(), estimated_covariance.ravel()))

    return rmse_diag, rmse_off_diag

# Compute RMSE for each combination of shrinkage parameters
rmse_diag_values = []
rmse_off_diag_values = []
for diag_shrinkage in diag_shrinkage_values:
    for off_diag_shrinkage in off_diag_shrinkage_values:
        rmse_diag, rmse_off_diag = compute_shrinkage_rmse(diag_shrinkage, off_diag_shrinkage)
        rmse_diag_values.append(rmse_diag)
        rmse_off_diag_values.append(rmse_off_diag)

# Reshape RMSE values to match the meshgrid shape
rmse_diag_values = np.array(rmse_diag_values).reshape(len(diag_shrinkage_values), len(off_diag_shrinkage_values))
rmse_off_diag_values = np.array(rmse_off_diag_values).reshape(len(diag_shrinkage_values), len(off_diag_shrinkage_values))

# Plot RMSE for diagonal shrinkage
plt.figure(figsize=(8, 3))
plt.imshow(rmse_diag_values, extent=(0, 1, 1, 0), aspect='auto', cmap='viridis')
plt.colorbar(label='RMSE')
plt.title('RMSE for Diagonal Shrinkage')
plt.xlabel('Off-diagonal Shrinkage')
plt.ylabel('Diagonal Shrinkage')
plt.show()

# Plot RMSE for off-diagonal shrinkage
plt.figure(figsize=(8, 3))
plt.imshow(rmse_off_diag_values, extent=(0, 1, 1, 0), aspect='auto', cmap='viridis')
plt.colorbar(label='RMSE')
plt.title('RMSE for Off-diagonal Shrinkage')
plt.xlabel('Off-diagonal Shrinkage')
plt.ylabel('Diagonal Shrinkage')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import ShrunkCovariance, OAS
from sklearn.metrics import mean_squared_error

# Parameters
n_features = 40  # Number of features
sample_size = 1000  # Sample size
shrinkage_values = np.linspace(0, 1, 20)  # Shrinkage values from 0 to 1

# Generate sample data
np.random.seed(42)
X_train = np.random.normal(size=(sample_size, n_features))

# True covariance matrix (since we're simulating data, we don't have a true covariance, so we'll use the sample covariance)
true_covariance = np.cov(X_train, rowvar=False)

# Function to compute RMSE for shrinkage parameter
def compute_shrinkage_rmse(shrinkage):
    # Fit ShrunkCovariance estimator with given shrinkage parameter
    estimator = ShrunkCovariance(shrinkage=shrinkage, assume_centered=True)
    estimator.fit(X_train)

    # Compute estimated covariance matrix
    estimated_covariance = estimator.covariance_

    # Compute RMSE for shrinkage parameter
    rmse = np.sqrt(mean_squared_error(true_covariance.ravel(), estimated_covariance.ravel()))

    return rmse

# Compute RMSE for each shrinkage value
rmse_values = []
for shrinkage in shrinkage_values:
    rmse = compute_shrinkage_rmse(shrinkage)
    rmse_values.append(rmse)

# Plot RMSE for shrinkage parameter
plt.figure(figsize=(8, 3))
plt.plot(shrinkage_values, rmse_values, marker='o', linestyle='-')
plt.title('RMSE for Shrinkage Parameter (ShrunkCovariance)')
plt.xlabel('Shrinkage Parameter')
plt.ylabel('RMSE')
plt.grid(True)
plt.show()

# Now, let's compare the performance of DOASD with OASD
# Define the DOASD estimator class with adaptive shrinkage
class DOASD(ShrunkCovariance):
    def __init__(self, diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1):
        super().__init__()
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def _compute_covariance(self, X):
        # Calculate the empirical covariance of X
        emp_cov = np.cov(X, rowvar=False)
        return emp_cov

    def fit(self, X, y=None):
        emp_cov = self._compute_covariance(X)
        n_features = emp_cov.shape[0]

        # Compute shrinkage factors
        diag_shrinkage = self.diagonal_shrinkage
        off_diag_shrinkage = self.off_diagonal_shrinkage

        # Apply shrinkage
        shrunk_diag_cov = emp_cov * (1 - diag_shrinkage) + np.diag(np.diag(emp_cov)) * diag_shrinkage
        shrunk_cov = shrunk_diag_cov * (1 - off_diag_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * off_diag_shrinkage

        self.covariance_ = shrunk_cov
        return self

# Fit DOASD estimator with default parameters
doasd_estimator = DOASD()
doasd_estimator.fit(X_train)

# Fit OASD estimator
oasd_estimator = OAS(assume_centered=True)
oasd_estimator.fit(X_train)

# Compute RMSE for DOASD
rmse_doasd = np.sqrt(mean_squared_error(true_covariance.ravel(), doasd_estimator.covariance_.ravel()))

# Compute RMSE for OASD
rmse_oasd = np.sqrt(mean_squared_error(true_covariance.ravel(), oasd_estimator.covariance_.ravel()))

# Plot performance comparison
plt.figure(figsize=(8, 3))
plt.bar(['DOASD', 'OASD'], [rmse_doasd, rmse_oasd], color=['blue', 'green'])
plt.title('Performance Comparison: DOASD vs OASD')
plt.xlabel('Estimator')
plt.ylabel('RMSE')
plt.grid(axis='y')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# Parameters
n_features = 40  # Number of features
sample_sizes = np.arange(6, 31)  # Sample sizes from 6 to 30

# Define a function to generate sample data with different variable scales
def generate_data(n_samples, n_features):
    base_X_train = np.random.normal(size=(n_samples, n_features))
    scaling_factors = np.arange(1, n_features + 1)
    X_train = base_X_train * scaling_factors
    return X_train

# Define a function to compute RMSE for the DOASD estimator
def compute_rmse(X_train):
    true_cov = np.cov(X_train, rowvar=False)
    emp_cov = np.cov(X_train, rowvar=False)

    # Compute shrinkage parameters
    n_samples = X_train.shape[0]
    diag_shrinkage = 1 - (n_features + 1) / n_samples
    off_diag_shrinkage = 1 - np.sum(np.diag(emp_cov)) / np.sum(emp_cov)

    # Apply shrinkage
    shrunk_diag_cov = emp_cov * (1 - diag_shrinkage) + np.diag(np.diag(emp_cov)) * diag_shrinkage
    shrunk_cov = shrunk_diag_cov * (1 - off_diag_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * off_diag_shrinkage

    # Compute RMSE
    rmse = np.sqrt(mean_squared_error(true_cov.ravel(), shrunk_cov.ravel()))
    return rmse

# Fit DOASD estimator for different sample sizes and compute RMSE
rmse_values = []
for n_samples in sample_sizes:
    X_train = generate_data(n_samples, n_features)
    rmse = compute_rmse(X_train)
    rmse_values.append(rmse)

# Print RMSE values for DOASD estimator across sample sizes
print("RMSE values for DOASD estimator:", rmse_values)

# Plot RMSE of DOASD estimator across sample sizes
plt.figure(figsize=(10, 6))
plt.plot(sample_sizes, rmse_values, label='DOASD', color='blue')
plt.title('RMSE of DOASD Estimator Across Sample Sizes')
plt.xlabel('Sample Size')
plt.ylabel('RMSE')
plt.legend()
plt.grid(True)
plt.show()

import numpy as np
import matplotlib.pyplot as plt

class DOASD:
    def __init__(self, diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1):
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        n_features = emp_cov.shape[0]

        # Compute shrinkage factors
        diag_shrinkage = self.diagonal_shrinkage
        off_diag_shrinkage = self.off_diagonal_shrinkage

        # Apply adaptive shrinkage
        shrunk_diag_cov = emp_cov * (1 - diag_shrinkage) + np.diag(np.diag(emp_cov)) * diag_shrinkage
        shrunk_cov = shrunk_diag_cov * (1 - off_diag_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * off_diag_shrinkage

        self.covariance_ = shrunk_cov
        return self

# Parameters
n_features = 40
n_samples = 1000

# Generate sample data
X_train = np.random.normal(size=(n_samples, n_features))

# Create DOASD estimator
doasd_estimator = DOASD(diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1)

# Fit DOASD estimator to data
doasd_estimator.fit(X_train)

# Plot original covariance matrix
plt.figure(figsize=(8, 4))
plt.subplot(1, 2, 1)
plt.imshow(np.cov(X_train, rowvar=False), cmap='hot', interpolation='nearest')
plt.title('Original Covariance Matrix')
plt.colorbar()

# Plot shrunk covariance matrix
plt.subplot(1, 2, 2)
plt.imshow(doasd_estimator.covariance_, cmap='hot', interpolation='nearest')
plt.title('Shrunk Covariance Matrix (DOASD)')
plt.colorbar()

plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance

class DOASD:
    def __init__(self, diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1):
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def fit(self, X):
        emp_cov = np.cov(X, rowvar=False)
        n_features = emp_cov.shape[0]

        # Compute shrinkage factors
        diag_shrinkage = self.diagonal_shrinkage
        off_diag_shrinkage = self.off_diagonal_shrinkage

        # Apply adaptive shrinkage
        shrunk_diag_cov = emp_cov * (1 - diag_shrinkage) + np.diag(np.diag(emp_cov)) * diag_shrinkage
        shrunk_cov = shrunk_diag_cov * (1 - off_diag_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * off_diag_shrinkage

        self.covariance_ = shrunk_cov
        return self

# Parameters
n_features = 40
n_samples = 1000

# Generate sample data
X_train = np.random.normal(size=(n_samples, n_features))

# Create DOASD estimator
doasd_estimator = DOASD(diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1)

# Fit DOASD estimator to data
doasd_estimator.fit(X_train)

# Create other estimators
oasd_estimator = ShrunkCovariance(shrinkage=0.5)
oas_estimator = OAS()
lw_estimator = LedoitWolf()

# Fit other estimators to data
oasd_estimator.fit(X_train)
oas_estimator.fit(X_train)
lw_estimator.fit(X_train)

# Plot original covariance matrix
plt.figure(figsize=(15, 5))
plt.subplot(1, 4, 1)
plt.imshow(np.cov(X_train, rowvar=False), cmap='hot', interpolation='nearest')
plt.title('Original Covariance Matrix')
plt.colorbar()

# Plot shrunk covariance matrices
plt.subplot(1, 4, 2)
plt.imshow(doasd_estimator.covariance_, cmap='hot', interpolation='nearest')
plt.title('DOASD')
plt.colorbar()

plt.subplot(1, 4, 3)
plt.imshow(oasd_estimator.covariance_, cmap='hot', interpolation='nearest')
plt.title('OASD')
plt.colorbar()

plt.subplot(1, 4, 4)
plt.imshow(lw_estimator.covariance_, cmap='hot', interpolation='nearest')
plt.title('Ledoit-Wolf')
plt.colorbar()

plt.show()

import numpy as np
import matplotlib.pyplot as plt
from sklearn.covariance import LedoitWolf, OAS, ShrunkCovariance
from sklearn.metrics import mean_squared_error

# Parameters
n_features = 40  # Number of features
sample_sizes = np.arange(6, 30)  # Sample sizes from 6 to 30

# Define a function to generate sample data with different variable scales
def generate_data(n_samples, n_features):
    base_X_train = np.random.normal(size=(n_samples, n_features))
    scaling_factors = np.arange(1, n_features + 1)
    X_train = base_X_train * scaling_factors
    return X_train

# Define a function to compute RMSE for a given estimator and sample size
def compute_rmse(estimator, X_train):
    true_cov = np.cov(X_train, rowvar=False)
    estimator.fit(X_train)
    estimated_cov = estimator.covariance_
    return np.sqrt(mean_squared_error(true_cov.ravel(), estimated_cov.ravel()))

# Define the DOASD estimator class with different levels of shrinkage
class DOASD(ShrunkCovariance):
    def __init__(self, diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1):
        super().__init__()
        self.diagonal_shrinkage = diagonal_shrinkage
        self.off_diagonal_shrinkage = off_diagonal_shrinkage

    def _compute_covariance(self, X):
        # Calculate the empirical covariance of X
        emp_cov = np.cov(X, rowvar=False)
        return emp_cov

    def fit(self, X, y=None):
        emp_cov = self._compute_covariance(X)
        n_features = emp_cov.shape[0]

        # Compute shrinkage factors
        diag_shrinkage = self.diagonal_shrinkage
        off_diag_shrinkage = self.off_diagonal_shrinkage

        # Apply shrinkage
        shrunk_diag_cov = emp_cov * (1 - diag_shrinkage) + np.diag(np.diag(emp_cov)) * diag_shrinkage
        shrunk_cov = shrunk_diag_cov * (1 - off_diag_shrinkage) + np.diag(np.diag(shrunk_diag_cov)) * off_diag_shrinkage

        self.covariance_ = shrunk_cov
        return self

# Fit covariance estimators for different sample sizes and compute RMSE
rmse_results = {'Ledoit-Wolf': [], 'OAS': [], 'OASD': [], 'DOASD': []}
for n_samples in sample_sizes:
    X_train = generate_data(n_samples, n_features)
    for estimator_name, estimator in [('Ledoit-Wolf', LedoitWolf()),
                                      ('OAS', OAS()),
                                      ('OASD', ShrunkCovariance(shrinkage=0.5)),
                                      ('DOASD', DOASD(diagonal_shrinkage=0.5, off_diagonal_shrinkage=0.1))]:
        rmse = compute_rmse(estimator, X_train)
        rmse_results[estimator_name].append(rmse)

# Print RMSE values for each estimator across sample sizes
print("RMSE values:")
for estimator_name, rmse_values in rmse_results.items():
    print(f"{estimator_name}: {rmse_values}")

# Plot RMSE across sample sizes for each estimator
plt.figure(figsize=(10, 6))
for estimator_name, rmse_values in rmse_results.items():
    plt.plot(sample_sizes, rmse_values, label=estimator_name)

plt.title('RMSE of Covariance Estimators Across Sample Sizes')
plt.xlabel('Sample Size')
plt.ylabel('RMSE')
plt.legend()
plt.grid(True)
plt.show()

