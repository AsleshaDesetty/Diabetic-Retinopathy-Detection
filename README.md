# Diabetic-Retinopathy-Detection Using EfficientNet

EfficientNet is a convolutional neural network built upon a concept called "compound scaling.” This concept addresses the longstanding trade-off between model size, accuracy, and computational efficiency. The idea behind compound scaling is to scale three essential dimensions of a neural network: width, depth, and resolution.

*Width*: Width scaling refers to the number of channels in each layer of the neural network. By increasing the width, the model can capture more complex patterns and features, resulting in improved accuracy. Conversely, reducing the width leads to a more lightweight model, suitable for low-resource environments.
*Depth*: Depth scaling pertains to the total number of layers in the network. Deeper models can capture more intricate representations of data, but they also demand more computational resources. On the other hand, shallower models are computationally efficient but may sacrifice accuracy.
*Resolution*: Resolution scaling involves adjusting the input image's size. Higher-resolution images provide more detailed information, potentially leading to better performance. However, they also require more memory and computational power. Lower-resolution images, on the other hand, consume fewer resources but may lead to a loss in fine-grained details.


Diabetic retinopathy is the leading cause of blindness in the working-age population of the developed world. It is estimated to affect over 93 million people.
Currently, detecting DR is a time-consuming and manual process that requires a trained clinician to examine and evaluate digital color fundus photographs of the retina. By the time human readers submit their reviews, often a day or two later, the delayed results lead to lost follow up, miscommunication, and delayed treatment.

Clinicians can identify DR by the presence of lesions associated with the vascular abnormalities caused by the disease. While this approach is effective, its resource demands are high. The expertise and equipment required are often lacking in areas where the rate of diabetes in local populations is high and DR detection is most needed. As the number of individuals with diabetes continues to grow, the infrastructure needed to prevent blindness due to DR will become even more insufficient.

The need for a comprehensive and automated method of DR screening has long been recognized, and previous efforts have made good progress using image classification, pattern recognition, and machine learning. With color fundus photography as input, the goal of this competition is to push an automated detection system to the limit of what is possible – ideally resulting in models with realistic clinical potential. The winning models will be open sourced to maximize the impact such a model can have on improving DR detection.
