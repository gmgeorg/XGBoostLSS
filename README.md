# XGBoostLSS - An extension of XGBoost to probabilistic forecasting
We propose a new framework of XGBoost that predicts the entire conditional distribution of a univariate response variable. In particular, **XGBoostLSS** models all moments of a parametric distribution, i.e., mean, location, scale and shape (LSS), instead of the conditional mean only. Choosing from a wide range of continuous, discrete and mixed discrete-continuous distribution, modeling and predicting the entire conditional distribution greatly enhances the flexibility of XGBoost, as it allows to gain additional insight into the data generating process, as well as to create probabilistic forecasts from which prediction intervals and quantiles of interest can be derived. 

## Motivation
Many regression / supervised models focus on the conditional mean only, implicitly treating higher moments of the conditional distribution as fixed nuisance parameters. This assumption, however, of constant higher moments not changing as functions of covariates is a stark one and is only valid in situations where the user is privileged with dealing with data generated by a symmetric Gaussian distribution with constant variance. In real world situations however, the data generating process is usually less well behaved, exhibiting characteristics such as heteroscedasticity, varying degrees of skewness and/or kurtosis. If the user sticks to his/her assumption of not modeling all characteristics of the data, inference as well as uncertainty assessments, such as confidence and predictions intervals, are at best invalid. In this context, the introduction of [Generalised Additive Models for Location Scale and Shape (GAMLSS)](https://www.gamlss.com/) has stimulated a lot of research and culminated in a new branch of statistics that focuses on modeling the entire conditional distribution as functions of covariates. Looking at the literature of more recent computer science and machine learning, however, the main focus has been on prediction accuracy and estimation speed. In fact, even though many recent machine learning approaches, like random forest or gradient boosting-type algorithms, outperform many statistical approaches when it comes to prediction accuracy, the output/forecast of these models provides information about the conditional mean only. Hence, these models are rather reluctant to reveal other characteristics of the (predicted) distribution and fall short in applications where a probabilistic forecasts is required, e.g., for assessing estimation/prediction uncertainty in form of confidence/prediction intervals.

In the era of increasingly awareness that the output of black box prediction models needs to be turned into explainable insights, our approach extends recent machine learning models to account for all distributional properties of the data. In particular, we focus on [XGBoost](https://github.com/dmlc/xgboost), which has gained much popularity and attention over the last years and has arguably become among the most widely used tools in practical data science. We term our model **XGBoostLSS**, as it combines the accuracy and speed of XGBoost with the flexibility of GAMLSS that allow for the estimation and prediction of the full conditional distribution. While retaining the speed of estimation and accuracy of XGBoost, **XGBoostLSS** allows the user to chose from a wide range of continuous, discrete and mixed discrete-continuous distributions to better adapt to the data at hand, as well as to provide predictive distributions, from which prediction intervals and quantiles can be derived. Furthermore, all XGBoost additions, such as partial dependent plots or the recently added [SHAP](https://github.com/slundberg/shap) (SHapley Additive exPlanations) approach that allows to explain the output of any machine learning model, are still applicable, with the additional advantage that they can be applied to all distributional parameter. As such, **XGBoostLSS** is intended to further close the gap between machine learning/computer science and statistics, so that models focusing mainly on prediction can also be used to describe and explain the underlying data generating process of the response of interest.

In the following, we provide a short walk-through of the functionality of **XGBoostLSS**. 

## Examples

### Simulation

We start with a simulated a data set that exhibits heteroscedasticity where the interest lies in predicting the 5% and 95% quantiles. The data is simulated as follows: 

```r
# Simulate
set.seed(123)
quant_sel <- c(0.05, 0.95)
n <- 10000
p <- 10
x <- runif(n)
y <- rnorm(n, mean = 10, sd = 1 + 4*(0.3 < x & x < 0.5) + 2*(x > 0.7))
X <- matrix(runif(n * p), ncol = p)
sim_data <- data.frame(y,x,X) 
dep_var <- "y"
covariates <- c("x", paste0("X", seq(1:10)))

# Split into train and test data
train_sample <- sample(1:n, floor(0.7*n))
train <- sim_data[train_sample, ]
test <- sim_data[-train_sample, ]
```

The dots in red show points that lie outside the 5% and 95% quantiles, which are indicated by the black dashed line.

![Optional Text](../master/plots/sim_data.png)

Let's fit an **XGBoostLSS** to the data. In general, the syntax is similar to the original XGBoost implementation. However, the user has to make a distributional assumption by specifying a family in the function call. As the data has been generated by a normal distribution, we use the Normal as a function input.

```r
# Data for XGBoostLSS
dtrain <- xgb.DMatrix(data = data.matrix(train[, covariates]),
                      label = train[, dep_var])
dtest <- xgb.DMatrix(data = data.matrix(test[, covariates]))
                     
# Fit model
xgblss_model <- xgblss.train(data = dtrain,
                             family = "NO",
                             n_init_hyper = 50,
                             time_budget = 10)
```

The user has also the option to provide a list of hyperparameters. In this example however, we use Bayesian Optimization as implemented in the [mlrMBO](https://github.com/mlr-org/mlrMBO) R-package, using a randomly generated set of initial hyperparameters that are used for training the surrogate Kriging model to find an optimized set of parameter. The *time_budget* parameter indicates the running time budget in minutes and is used as a stopping criteria for the Bayesian Optimization.

Once the model is trained, we can predict all parameter of the distribution.                 
   
                    
```r
# Predict
xgblss_mu_pred <- predict(xgblss_model,
                          newdata = dtest,
                          parameter = "mu")
                          
xgblss_sigma_pred <- predict(xgblss_model,
                             newdata = dtest,
                             parameter = "sigma")

```

As **XGBoostLSS** allows to model the entire conditional distribution, we can draw random samples from the predicted distribution, which allows us to create prediction intervals and quantiles of interest. The below image shows the predictions of **XGBoostLSS** for the 5% and 95% quantile in blue. 

![Optional Text](../master/plots/xgboostlss_sim.png)

Comparing the coverage of the intervals with the nominal level of 90% shows that **XGBoostLSS** not only correctly models the heteroscedasticity in the data, but it also provides an accurate forecast for the 5% and 95% quantiles. The great flexibility of **XGBoostLSS** also comes from its ability to provide attribute importance, as well as partial dependence plots for all of the distributional parameters. In the following we only investigate the effect on the conditional variance. All plots are generated using wrappers around the [interpretable machine learning (iml)](https://github.com/christophM/iml) R package.

```r
# Shapley value
plot(xgblss_model,
     parameter = "mu",
     type = "shapley")
```

![Optional Text](../master/plots/xgboostlss_shapley.png)

The plot of the Shapley value shows that **XGBoostLSS** has identified the only informative predictor *x* and does not consider any of the noise variables X1, ..., X10 as an important feature. 


```r
# Partial Dependence Plots
plot(xgblss_model,
     parameter = "mu",
     type = "pdp")
```
Looking at partial dependence plots of the effect of x on Var(y|x) shows that it also correctly identifies the amount of heteroscedasticity in the data.

![Optional Text](../master/plots/xgboostlss_parteffect.png)

###  Data for the Rent Index 2003 in Munich, Germany

![Optional Text](../master/plots/munich_rent_district.png)

In this example we show the usage of **XGBoostLSS** using a sample of 2,053 apartments from the data collected for the preparation of the Munich rent index 2003.

- *rent*
  - Net rent in EUR (numeric).

- *rentsqm*
  - Net rent per square meter in EUR (numeric).

- *area*
  - Floor area in square meters (numeric).

- *rooms*
  - Number of rooms (numeric).

- *yearc*
  - Year of construction (numeric).

- *bathextra*
  - Factor: High quality equipment in the bathroom?

- *bathtile*
  - Factor: Bathroom tiled?

- *cheating*
  - Factor: Central heating available?

- *district*
  - Urban district where the apartment is located. Factor with 25 levels: "All-Umenz" (Allach - Untermenzing), "Alt-Le" (Altstadt - Lehel), "Au-Haid" (Au - Haidhausen), "Au-Lo-La" (Aubing - Lochhausen - Langwied), "BamLaim" (Berg am Laim), "Bogenh" (Bogenhausen), "Feld-Has" (Feldmoching - Hasenbergl), "Had" (Hadern), "Laim" (Laim), "Lud-Isar"(Ludwigsvorstadt - Isarvorstadt), "Maxvor" (Maxvorstadt), "Mil-AmH" (Milbertshofen - Am Hart), "Moos" (Moosach), "Neuh-Nymp" (Neuhausen - Nymphenburg), "Obgies" (Obergiesing), "Pas-Obmenz" (Pasing - Obermenzing), "Ram-Per" (Ramersdorf - Perlach), "SchwWest" (Schwabing West), "Schwab-Frei" (Schwabing - Freimann), "Schwanth" (Schwanthalerhoehe), "Send" (Sendling), "Send-West" (Sendling - Westpark), "Th-Ob-Fo-Fu-So" (Thalkirchen - Obersendling - Forstenried - Fuerstenried - Solln), "Trud-Riem" (Trudering - Riem) and "Ugies-Har" (Untergiesing - Harlaching).

- *location*
  - Quality of location. Ordered factor with levels "normal", "good" and "top".

- *upkitchen*
  - Factor: Upscale equipment in kitchen?

- *wwater*
  - Factor: Hot water supply available?

```r
# Load data
data("munichrent03", package = "LinRegInteractive")

munichrent03 <- munichrent03 %>% 
  select(-rent) %>% 
  mutate_if(is.integer, as.numeric)
  
# Dummy Coding
munichrent03_dummy <- munichrent03 %>% 
  mlr::createDummyFeatures(target = dep_var)

# Train and Test Data 
set.seed(123)
train_split <- sample(1:nrow(munichrent03), floor(0.7*nrow(munichrent03)))
train <- munichrent03_dummy[train_split,]
test <- munichrent03_dummy[-train_split,]

# Select dependent variable and covariates
covariates <- munichrent03_dummy %>% 
  select(-dep_var) %>% 
  colnames()  
dep_var <- "rentsqm"

# Data for XGBoostLSS
dtrain <- xgb.DMatrix(data = data.matrix(train[, covariates]),
                      label = train[, dep_var])
dtest <- xgb.DMatrix(data = data.matrix(test[, covariates]))
```

The first decision one has to make is about choosing an appropriate distribution for the response. As there are many potential candidates, we use an automated approach based on the generalised Akaike information criterion. Due to its great flexibility, many functions of the R package [gamlss](https://cran.r-project.org/web/packages/gamlss/index.html) are used within **XGBoostLSS**. 

```r
opt_dist <- fitDist(y = train[, dep_var],
                    type = "realplus",
                    extra = "NO")              
                 
      dist    GAIC
1      GB2 6588.29
2       NO 6601.17
3       GG 6602.02
4     BCCG 6602.26
5      WEI 6602.37
6   exGAUS 6603.17
7      BCT 6603.35
8    BCPEo 6604.26
9       GA 6707.85
10     GIG 6709.85
11   LOGNO 6839.56
12      IG 6871.12
13  IGAMMA 7046.50
14     EXP 9018.04
15 PARETO2 9020.04
16      GP 9020.05

```

Even though the generalized Beta type 2 provides the best approximation to the data, we use the more parsimonious Normal distribution, as it has only two distributional parameter, compared to 4 of the generalized Beta type 2. In general, though, **XGBoostLSS** is flexible to allow the use to chose and fit all distributions available in the [gamlss](https://cran.r-project.org/web/packages/gamlss/index.html) package. The good fit of the Normal distribution is also confirmed by the following density plot, where the actual data is presented as a histogrom, while the normal fit is shown in red.

![Optional Text](../master/plots/fitted_dist.png)

Now that we have specified the distribution, let's fit an **XGBoostLSS** to the data.

```r
# Fit model
xgblss_model <- xgblss.train(data = dtrain,
                             family = "NO",
                             n_init_hyper = 50,
                             time_budget = 5)
```
Again, we use Bayesian Optimization for finding an optimal set of hyperparameter, while restricting the overall runtime to 5 minutes.                
```r
# Shapley value
plot(xgblss_model,
     parameter = "all",
     type = "shapley")
```

Looking at the top 5 Shapley values for both the conditional mean and variance indicates that both *yearc* and *area* are considered as being important variables.

![Optional Text](../master/plots/munich_rent_shapley.png)

Looking at the estimated effects indicates that newer flats are on average more expensive, with the variance first decreasing and increasing again for flats built around 1980 and later. Also, as expected, rents per square meter decrease with an increasing size of the appartment.  

```r
# Partial Dependence Plots
plot(xgblss_model,
     parameter = "all",
     type = "pdp")
```

![Optional Text](../master/plots/munich_rent_estimated_effects.png)

As we have modelled all parameter of the Normal distribution, **XGBoostLSS** provides a probabilistic forecast, from which any quantity of interest can be derived. The following shows a subset of 50 predictions only for ease of readability. The red dots show the actual rents, while the boxplots are the distributional predictions.

![Optional Text](../master/plots/munich_rent_pred_boxplot.png)


### Comparison to other approaches
To evaluate the prediction accuracy of **XGBoostLSS**, we compare the forecasts of the Munich rent example to the implementations available in [gamlss](https://cran.r-project.org/web/packages/gamlss/index.html) and in [gamboostLSS](https://cran.r-project.org/package=gamboostLSS). For both implementations, we use factor coding, instead of dummy-coding as for **XGBoostLSS**.


```r
# XGBoostLSS predictions
xgblss_mu_pred <- predict(xgblss_model,
                          newdata = dtest,
                          parameter = "mu")
                          
xgblss_sigma_pred <- predict(xgblss_model,
                             newdata = dtest,
                             parameter = "sigma")

# Data for gamlss models
train_gamlss <- munichrent03[train_split,]
test_gamlss <- munichrent03[-train_split,]
gamlss_form <- as.formula(paste(dep_var, "~ ."))

# gamboostLSS
covariates_gamlss <- munichrent03 %>% 
  dplyr::select(-dep_var) %>% 
  colnames()

gamboostLSS_form <- as.formula(paste0(dep_var, "~",
                                    paste0("bbs(", covariates_gamlss[1:3], ")", collapse = "+"),
                                    "+",
                                    paste0("bols(", covariates_gamlss[4:length(covariates_gamlss)], ")", collapse = "+")))
                                    
# rentsqm ~ bbs(area) + bbs(rooms) + bbs(yearc) + bols(bathextra) + bols(bathtile) + 
# bols(cheating) + bols(district) + bols(location) + bols(upkitchen) + bols(wwater)

gamboostlss_mod <- gamboostLSS(list(mu = gamboostLSS_form,
                                                  sigma = gamboostLSS_form),
                                             families = GaussianLSS(),
                                             control = boost_control(mstop = 5000,
                                                                     nu = 0.1),
                                             method = "noncyclic",
                                             data = train_gamlss)

set.seed(123)
cl <- parallel::makeCluster(detectCores() - 1) 
myApply <- function(X, FUN, ...) {
  myFun <- function(...) {
    library("mboost") 
    FUN(...)
  }
  parLapply(cl = cl, X, myFun, ...)
}

cv10f <- cv(model.weights(gamboostlss_mod), type = "kfold")
cv_model <- cvrisk(gamboostlss_mod,
                   folds = cv10f,
                   papply = myApply)
stopCluster(cl)

gamboostlss_mod_cv <- gamboostlss_mod[mstop(cv_model)] 

gamboostlss_mod_mu_pred <- as.numeric(predict(gamboostlss_mod_cv,
                                              newdata = test_gamlss,
                                              type = "response",
                                              parameter = "mu")) 

gamboostlss_mod_sigma_pred <- as.numeric(predict(gamboostlss_mod_cv,
                                                 newdata = test_gamlss,
                                                 type = "response",
                                                 parameter = "sigma"))
                                                 
                                                 
                                                 
# GAMLSS
gamlss_form_mu <- as.formula(paste0(dep_var, "~",
                                    paste0("pb(", covariates_gamlss[1:3], ")", collapse = "+"),
                                    "+",
                                    paste0(covariates_gamlss[4:length(covariates_gamlss)], collapse = "+")))
                                    
                                    
# rentsqm ~ pb(area) + pb(rooms) + pb(yearc) + bathextra + bathtile + 
#    cheating + district + location + upkitchen + wwater
    

gamlss_form_lss <- as.formula(paste0("~",
                                     paste0("pb(", covariates_gamlss[1:3], ")", collapse = "+"),
                                     "+",
                                     paste0(covariates_gamlss[4:length(covariates_gamlss)], collapse = "+")))


gamlss_model <- gamlss(gamlss_form_mu,
                       sigma.formula = gamlss_form_lss,
                       family = "NO",
                       data = train_gamlss)

gamlss_mu_pred <- predictAll(gamlss_model,
                             type = "response",
                             newdata = test_gamlss)$mu

gamlss_sigma_pred <- predictAll(gamlss_model,
                             type = "response",
                             newdata = test_gamlss)$sigma

```

We evaluate distributional forecasts using Continuous Ranked Probability Scoring Rules (CRPS) implemented in the [scoringRules](https://cran.r-project.org/web/packages/scoringRules/index.html) R-package, where lower scores indicates a better forecast, along with a Mean Absolute Error (MAE) comparison evaluating the mean-prediction accuracy of the models.

```r
            CRPS-Score      MAE
XGBoostLSS    1.139325 1.608783
gamboostLSS   1.154054 1.627551
gamlss        1.152746 1.625110
```

Both CRPS and MAE indicate that XGBoostLSS provides more accurate forecasts than the other two approaches.

### Software Implementations
In its current implementation, **XGBoostLSS** is available in *R* only, but extensions to *Julia* and *Python* are in progress.



## References
März, Alexander (2019). *"XGBoostLSS - An extension of XGBoost to probabilistic forecasting"*. pp. 1–26. *Under Review*.
