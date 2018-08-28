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
