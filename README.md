data/caffe2_nodes.csv

ATen (Experimental)                       |  Failed!
------------------------------------------|--------------------------
Abs                                       |  Passed!
Acos                                      |  Passed!
Add                                       |  Passed!
Affine (Experimental)                     |  Failed!
And                                       |  Passed!
ArgMax                                    |  Passed!
ArgMin                                    |  Passed!
ArrayFeatureExtractor                     |  Failed!
Asin                                      |  Passed!
Atan                                      |  Passed!
AveragePool                               |  Passed!
BatchNormalization                        |  Passed!
Binarizer                                 |  Failed!
Cast                                      |  Failed!
CastMap                                   |  Failed!
CategoryMapper                            |  Failed!
Ceil                                      |  Passed!
Clip                                      |  Passed!
Concat                                    |  Passed!
Constant                                  |  Passed!
ConstantFill (Experimental)               |  Passed!
Conv                                      |  Passed!
ConvTranspose                             |  Passed!
Cos                                       |  Passed!
Crop (Experimental)                       |  Failed!
DepthToSpace                              |  Failed!
DictVectorizer                            |  Failed!
Div                                       |  Passed!
Dropout                                   |  Passed!
Elu                                       |  Passed!
Equal                                     |  Passed!
Exp                                       |  Passed!
Expand                                    |  Passed!
FeatureVectorizer                         |  Failed!
Flatten                                   |  Passed!
Floor                                     |  Passed!
GRU                                       |  Failed!
GRUUnit (Experimental)                    |  Failed!
Gather                                    |  Passed!
Gemm                                      |  Passed!
GivenTensorFill (Experimental)            |  Failed!
GlobalAveragePool                         |  Passed!
GlobalLpPool                              |  Failed!
GlobalMaxPool                             |  Passed!
Greater                                   |  Passed!
HardSigmoid                               |  Failed!
Hardmax                                   |  Failed!
Identity                                  |  Passed!
If                                        |  Failed!
ImageScaler (Experimental)                |  Failed!
Imputer                                   |  Failed!
InstanceNormalization                     |  Passed!
LRN                                       |  Passed!
LSTM                                      |  Passed!
LabelEncoder                              |  Failed!
LeakyRelu                                 |  Passed!
Less                                      |  Passed!
LinearClassifier                          |  Failed!
LinearRegressor                           |  Failed!
Log                                       |  Passed!
LogSoftmax                                |  Passed!
Loop                                      |  Failed!
LpNormalization                           |  Failed!
LpPool                                    |  Failed!
MatMul                                    |  Passed!
Max                                       |  Passed!
MaxPool                                   |  Passed!
MaxRoiPool                                |  Failed!
Mean                                      |  Passed!
MeanVarianceNormalization (Experimental)  |  Failed!
Min                                       |  Passed!
Mul                                       |  Passed!
Multinomial                               |  Failed!
Neg                                       |  Passed!
Normalizer                                |  Failed!
Not                                       |  Passed!
OneHotEncoder                             |  Failed!
Or                                        |  Passed!
PRelu                                     |  Passed!
Pad                                       |  Passed!
ParametricSoftplus (Experimental)         |  Failed!
Pow                                       |  Passed!
RNN                                       |  Passed!
RandomNormal                              |  Failed!
RandomNormalLike                          |  Failed!
RandomUniform                             |  Failed!
RandomUniformLike                         |  Failed!
Reciprocal                                |  Passed!
ReduceL1                                  |  Failed!
ReduceL2                                  |  Failed!
ReduceLogSum                              |  Failed!
ReduceLogSumExp                           |  Failed!
ReduceMax                                 |  Passed!
ReduceMean                                |  Passed!
ReduceMin                                 |  Passed!
ReduceProd                                |  Failed!
ReduceSum                                 |  Passed!
ReduceSumSquare                           |  Failed!
Relu                                      |  Passed!
Reshape                                   |  Passed!
SVMClassifier                             |  Failed!
SVMRegressor                              |  Failed!
Scale (Experimental)                      |  Failed!
ScaledTanh (Experimental)                 |  Failed!
Scaler                                    |  Failed!
Scan                                      |  Failed!
Selu                                      |  Passed!
Shape                                     |  Passed!
Sigmoid                                   |  Passed!
Sin                                       |  Passed!
Size                                      |  Passed!
Slice                                     |  Passed!
Softmax                                   |  Passed!
Softplus                                  |  Passed!
Softsign                                  |  Passed!
SpaceToDepth                              |  Failed!
Split                                     |  Passed!
Sqrt                                      |  Passed!
Squeeze                                   |  Passed!
Sub                                       |  Passed!
Sum                                       |  Passed!
Tan                                       |  Passed!
Tanh                                      |  Passed!
ThresholdedRelu (Experimental)            |  Passed!
Tile                                      |  Failed!
TopK                                      |  Passed!
Transpose                                 |  Passed!
TreeEnsembleClassifier                    |  Failed!
TreeEnsembleRegressor                     |  Failed!
Unsqueeze                                 |  Passed!
Upsample                                  |  Passed!
Xor                                       |  Passed!
ZipMap                                    |  Failed!
Summary                                   |  81/134 node tests passed

data/caffe2_models.csv

resnet50        |  9/9 nodes covered: Passed!
----------------|------------------------------
bvlc_alexnet    |  8/8 nodes covered: Passed!
inception_v2    |  12/12 nodes covered: Passed!
squeezenet_old  |  7/7 nodes covered: Passed!
inception_v1    |  10/10 nodes covered: Passed!
vgg19           |  7/7 nodes covered: Passed!
shufflenet      |  11/11 nodes covered: Passed!
densenet121     |  10/10 nodes covered: Passed!
Summary         |  8/8 model tests passed
Op                                        |  tensorflow                |  caffe2
------------------------------------------|----------------------------|--------------------------
ATen (Experimental)                       |  Failed!                   |  Failed!
Abs                                       |  Passed!                   |  Passed!
Acos                                      |  Passed!                   |  Passed!
Add                                       |  Passed!                   |  Passed!
Affine (Experimental)                     |  Failed!                   |  Failed!
And                                       |  Passed!                   |  Passed!
ArgMax                                    |  Passed!                   |  Passed!
ArgMin                                    |  Passed!                   |  Passed!
Asin                                      |  Passed!                   |  Passed!
Atan                                      |  Passed!                   |  Passed!
AveragePool                               |  Passed!                   |  Passed!
BatchNormalization                        |  Passed!                   |  Passed!
Cast                                      |  Passed!                   |  Failed!
Ceil                                      |  Passed!                   |  Passed!
Clip                                      |  Passed!                   |  Passed!
Concat                                    |  Passed!                   |  Passed!
Constant                                  |  Passed!                   |  Passed!
ConstantFill (Experimental)               |  Passed!                   |  Passed!
Conv                                      |  Passed!                   |  Passed!
ConvTranspose                             |  Passed!                   |  Passed!
Cos                                       |  Passed!                   |  Passed!
Crop (Experimental)                       |  Failed!                   |  Failed!
DepthToSpace                              |  Passed!                   |  Failed!
Div                                       |  Passed!                   |  Passed!
Dropout                                   |  Passed!                   |  Passed!
Elu                                       |  Passed!                   |  Passed!
Equal                                     |  Passed!                   |  Passed!
Exp                                       |  Passed!                   |  Passed!
Expand                                    |  Passed!                   |  Passed!
Flatten                                   |  Passed!                   |  Passed!
Floor                                     |  Passed!                   |  Passed!
GRU                                       |  Passed!                   |  Failed!
GRUUnit (Experimental)                    |  Failed!                   |  Failed!
Gather                                    |  Passed!                   |  Passed!
Gemm                                      |  Passed!                   |  Passed!
GivenTensorFill (Experimental)            |  Failed!                   |  Failed!
GlobalAveragePool                         |  Passed!                   |  Passed!
GlobalLpPool                              |  Failed!                   |  Failed!
GlobalMaxPool                             |  Passed!                   |  Passed!
Greater                                   |  Passed!                   |  Passed!
HardSigmoid                               |  Passed!                   |  Failed!
Hardmax                                   |  Passed!                   |  Failed!
Identity                                  |  Passed!                   |  Passed!
If                                        |  Failed!                   |  Failed!
ImageScaler (Experimental)                |  Failed!                   |  Failed!
InstanceNormalization                     |  Passed!                   |  Passed!
LRN                                       |  Passed!                   |  Passed!
LSTM                                      |  Passed!                   |  Passed!
LeakyRelu                                 |  Passed!                   |  Passed!
Less                                      |  Passed!                   |  Passed!
Log                                       |  Passed!                   |  Passed!
LogSoftmax                                |  Passed!                   |  Passed!
Loop                                      |  Failed!                   |  Failed!
LpNormalization                           |  Failed!                   |  Failed!
LpPool                                    |  Failed!                   |  Failed!
MatMul                                    |  Passed!                   |  Passed!
Max                                       |  Passed!                   |  Passed!
MaxPool                                   |  Passed!                   |  Passed!
MaxRoiPool                                |  Failed!                   |  Failed!
Mean                                      |  Passed!                   |  Passed!
MeanVarianceNormalization (Experimental)  |  Failed!                   |  Failed!
Min                                       |  Passed!                   |  Passed!
Mul                                       |  Passed!                   |  Passed!
Multinomial                               |  Failed!                   |  Failed!
Neg                                       |  Passed!                   |  Passed!
Not                                       |  Passed!                   |  Passed!
Or                                        |  Passed!                   |  Passed!
PRelu                                     |  Passed!                   |  Passed!
Pad                                       |  Passed!                   |  Passed!
ParametricSoftplus (Experimental)         |  Failed!                   |  Failed!
Pow                                       |  Passed!                   |  Passed!
RNN                                       |  Passed!                   |  Passed!
RandomNormal                              |  Failed!                   |  Failed!
RandomNormalLike                          |  Failed!                   |  Failed!
RandomUniform                             |  Failed!                   |  Failed!
RandomUniformLike                         |  Failed!                   |  Failed!
Reciprocal                                |  Passed!                   |  Passed!
ReduceL1                                  |  Passed!                   |  Failed!
ReduceL2                                  |  Passed!                   |  Failed!
ReduceLogSum                              |  Passed!                   |  Failed!
ReduceLogSumExp                           |  Passed!                   |  Failed!
ReduceMax                                 |  Passed!                   |  Passed!
ReduceMean                                |  Passed!                   |  Passed!
ReduceMin                                 |  Passed!                   |  Passed!
ReduceProd                                |  Passed!                   |  Failed!
ReduceSum                                 |  Passed!                   |  Passed!
ReduceSumSquare                           |  Passed!                   |  Failed!
Relu                                      |  Passed!                   |  Passed!
Reshape                                   |  Passed!                   |  Passed!
Scale (Experimental)                      |  Failed!                   |  Failed!
ScaledTanh (Experimental)                 |  Failed!                   |  Failed!
Scan                                      |  Failed!                   |  Failed!
Selu                                      |  Passed!                   |  Passed!
Shape                                     |  Passed!                   |  Passed!
Sigmoid                                   |  Passed!                   |  Passed!
Sin                                       |  Passed!                   |  Passed!
Size                                      |  Passed!                   |  Passed!
Slice                                     |  Passed!                   |  Passed!
Softmax                                   |  Passed!                   |  Passed!
Softplus                                  |  Passed!                   |  Passed!
Softsign                                  |  Passed!                   |  Passed!
SpaceToDepth                              |  Failed!                   |  Failed!
Split                                     |  Passed!                   |  Passed!
Sqrt                                      |  Passed!                   |  Passed!
Squeeze                                   |  Passed!                   |  Passed!
Sub                                       |  Passed!                   |  Passed!
Sum                                       |  Passed!                   |  Passed!
Tan                                       |  Passed!                   |  Passed!
Tanh                                      |  Passed!                   |  Passed!
ThresholdedRelu (Experimental)            |  Passed!                   |  Passed!
Tile                                      |  Passed!                   |  Failed!
TopK                                      |  Passed!                   |  Passed!
Transpose                                 |  Passed!                   |  Passed!
Unsqueeze                                 |  Passed!                   |  Passed!
Upsample                                  |  Passed!                   |  Passed!
Xor                                       |  Passed!                   |  Passed!
Summary                                   |  93/116 node tests passed  |  81/116 node tests passed

Model           |  tensorflow                    |  caffe2
----------------|--------------------------------|------------------------------
resnet50        |  9/9 nodes covered: Passed!    |  9/9 nodes covered: Passed!
bvlc_alexnet    |  8/8 nodes covered: Passed!    |  8/8 nodes covered: Passed!
inception_v2    |  12/12 nodes covered: Passed!  |  12/12 nodes covered: Passed!
squeezenet_old  |  7/7 nodes covered: Passed!    |  7/7 nodes covered: Passed!
inception_v1    |  10/10 nodes covered: Passed!  |  10/10 nodes covered: Passed!
vgg19           |  7/7 nodes covered: Passed!    |  7/7 nodes covered: Passed!
shufflenet      |  11/11 nodes covered: Passed!  |  11/11 nodes covered: Passed!
densenet121     |  10/10 nodes covered: Passed!  |  10/10 nodes covered: Passed!
Summary         |  8/8 model tests passed        |  8/8 model tests passed
\n\n
# Adding Another Backend to the Scoreboard

To add another backend to the scoreboard, simply modify the Dockerfile [here](https://github.com/Ac2zoom/dockerfiles/blob/scoreboard/onnx-docker/onnx-docker-cpu/Dockerfile) to also install the relevant framework and backend.  Once this is done, add a call to pytest for the relevant test (subclass of [onnx.backend.test](https://github.com/onnx/onnx/tree/master/onnx/backend/test)) to [.travis.yml](https://github.com/Ac2zoom/onnx-backend-scoreboard/blob/master/.travis.yml).  Ensure that, before this test is run, `export BACKEND='<backend name>'` is added to the travis command in the Docker container before pytest is called.  This will ensure that the correct files are written.  Once this is done, the Travis CI will automatically generate the correct files and write to both the README and the CSV files rendered by the GitHub Page.
