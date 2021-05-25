# Cyber WOLF
Web application Offensive Learning Firewall

## Abstract
Cyber WOLF is a Web Application Firewall (WAF) that leverages Machine Learning to detect and neutralize cyberattacks.
Contrary to most ML based WAF's, Cyber WOLF does not black list attack signatures.
Cyber WOLF uses ML to "learn" the signatures of normal HTTP requests.
This white list is then used to evaluate incoming requests before sending them to you web application.
Once the model is sufficiently trained, the model can be deployed in a WAF environment.
Here the model will judge each request's signature and will either allow, flag or deny a request based on the prediction of our ML model.
Although the model judges application layer HTTP requests, Cyber WOLF is implemented on the TCP layer of communications.
This package contains:
- A custom HTTP parser as part of [the preprocessor](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_preprocessor.py).
- A [model building/training script](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_training.py), powered by Tensorflow Keras.
- A [validation script](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_validation.py) to evaluate your model with, based on custom cyber attacks, before deployment.
- A configurable [Web Application Firewall (WAF)](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/cyberwolf.py).
- Some configuration files

## How does it work?
Cyber WOLF is a reverse proxy. This means that you install Cyber WOLF as a public endpoint in your network. You must then configure the location of your web application, which should only accept connections from Cyber WOLF. Cyber WOLF listens to HTTP requests and after evaluating, passes them on to your webapplication. If everything is well, Cyber WOLF will then return the HTTP response from your web application back to you. If a cyber attack is detected in the HTTP request, Cyber WOLF will drop the TCP conection and inform the caller that their request has been denied.

In order to corectly set up Cyber WOLF you need to undertake a few steps:
- Create a detection model
- Maybe evaluate your model
- Configure Cyber WOLF
- Let it ride baby

### Creating a detection model
Because every web application is different Cyber WOLF needs to learn correct signatures for your web application. This can be done by using a simple tool like [TCP Proxy](https://github.com/Mathuiss/tcp_proxy). In the future this dataset should be created for you by Cyber WOLF, but this is release 0.1. For a small web application a data set of around 250 requests should suffice. If you have a bigger web application you should propably leave the TCP proxy on for a little longer. After gathering the raw HTTP requests, you must use the [preprocessor](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_preprocessor.py) to create your data set for you. Now it is time to run 
