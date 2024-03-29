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
- Setting up your production environment

### Creating a detection model
Because every web application is different Cyber WOLF needs to learn correct signatures for your web application. This can be done by using a simple tool like [TCP Proxy](https://github.com/Mathuiss/tcp_proxy). In the future this dataset should be created for you by Cyber WOLF, but this is release 0.1. For a small web application a data set of around 250 requests should suffice. If you have a bigger web application you should propably leave the TCP proxy on for a little longer. After gathering the raw HTTP requests, you must use the [preprocessor](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_preprocessor.py) to create your data set for you. Now it is time to run the [training script](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_training.py) and build your model.

### Evaluating your model
The [validation script](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_validation.py) allows you to run a few pre-defined HTTP requests through your model and simulate a live environment. It will display the results verbosely so you can easily spot where adjustments need to be made.

### Configure Cyber WOLF
The configuration of Cyber WOLF consists of 3 files:
- [cyberwolf.config](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/cyberwolf.config)
- [cyberwolf.ignore](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/cyberwolf.ignore)
- [cyberwolf.flags](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/cyberwolf.flags)

#### cyberwolf.config
This configuration file allows you to specify important paths and other variables, which are used by the preprocessor, the training script and the firewall.
```
dataset_path=/home/mathuis/Development/cyber_wolf/data/datasets
ignore_file=/home/mathuis/Development/cyber_wolf/rel/cyberwolf.ignore
request_path=/home/mathuis/Development/cyber_wolf/data/requests
model_path=/home/mathuis/Development/cyber_wolf/data/models
model_name=best-class-model.h5
epsilon=0.45
threshd=0.1
adversarial_path=/home/mathuis/Development/cyber_wolf/data/adversarial
```
This config file consists of a list of key-value pairs seperated by the ```=``` sign.
The ```epsilon``` value specifies the sensitivity of the blocking ratio.
The ```threshd``` value specifies the sensitivity of detection mechanism.
Both of these values will be explained later.

#### cyberwolf.ignore
If your web application uses headers or other values which can poison the training data, these can be added to the ignore file.
You should not specify any fields which make your application vulnerable to cyber attacks, such as ```username``` or ```password```.

#### cyberwolf.flags
If a value is flagged by Cyber WOLF but not outright blocked, the value will appear in the flags list. This list allows administrators to check if any cyber attacks have been carried out, which were not detected by Cyber WOLF's blocking mechanism.

### Setting up your production environment
Now that you have configured Cyber WOLF it is time to enter into production. Copy the ```rel/``` directory to the location from where you want to deploy the firewall.
Start the fire wall with the command:
```bash
./cyberwolf
```
One you see a message like ```Listening for incoming connections on 0.0.0.0:8000``` you can start sending HTTP requests to your web application.

## TODO:
Here is the list of features that are not yet implemented in this release:
- Automatic data gathering (saving the first n number of HTTP requests to train the model on).
- Audtomatic model building (automatically building an deploying a model based on the traffic it has saved during the gathering phase).
- Flagging interface (allowing admins to easily allow or block values that have been flagged for review).
- Multi-threaded connection handling

This was all the nessecary information in order for you to get started using Cyber WOLF. If you want to know more about the theory behind this software, please continue reading the next chapter.

## Under the hood of Cyber WOLF
In this chapter we will look at the way our machine learning algorithm is implemented. Furthermore we will take a look at the way feature extraction is implemented and why. We will also look at the way the model is built and it's performance. Lastly we will take a look at the way the detection algorithm is implemented and why it works like that.

### Machine learning
Cyber attacks on web applications come in 2 categories: Context-dependent and context-independent cyber attacks. A context-dependent cyber attacks is an attack which is not visible in the data. For examle if a hacker performs a login action with a correct user name and password, we are unable to determine whether this is a cyber attack or not, by looking at the HTTP request alone. A context-independent cyber attack on the other hand is recognizable by looking at an HTTP request.
```
POST /EditPosition?handler=Buy HTTP/1.1
Host: localhost:8000
Connection: keep-alive
Content-Length: 246
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://localhost:8000
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-GPC: 1
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9


ClientId=%3CSCRIPT%20TYPE=%22TEXT/JAVASCRIPT%22%3EVAR%20ADR%20=%20%27../EVIL.PHP?CAKEMONSTER=%27%20+%20ESCAPE(DOCUMENT.COOKIE);%3C/SCRIPT%3E&Item=2&amount=20
```
By looking at the above HTTP request a human is easily able to spot the XSS payload in the request body. A machine learning model can be trained to specifically detect an XSS, SQLi or any other payload. These types of firewalls already exist and can be downloaded for free on github. Our goal is to build a machine learning model that is able to detect anomalies in HTTP requests, and take certain actions based on the certainty of it being a cyber attack.

As stated above we will rely on the anomaly detection strategy to learn features of benign HTTP requests to a specific web application, so that we can compare these signatures to incoming requests and detect statistical outliers. This way we can simply white-list types of traffic and perform a specific action on divergent requests. The anomaly detection method has a few benefits over the traditional categorical models. Namely that there is no need for a comprehensive data set of cyber attacks from which to learn but also that we can hopefully detect cyber attacks that do not yet exist, due to the white listing of benign traffic.

To build our anomaly detection algorithm we require 3 things:
- A data set containing enough benign HTTP request from which to learn
- A sound feature extraction method that captures the requests signature
- A neural network that is able to compress data into it's latent space representation and from that learn how to rebuild the data into it's original dimensional state

### Feature extraction
Feature extraction is done as part of the [preprocessor](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_preprocessor.py). To be able to capture the essence of the data a rather simple technique is used. We will scan the request and find all user controled input. This means that we will parse all query parameters, header values and body values. These are all stored in a big list. Then the program will parse these requests and build a histogram for each value with the following specification:
```python
FEATUE_DEF = ["path", "header", "body", "length", "lowercase", "uppercase", "0", "1", "2", "3", "4", "5", "6", "7",
            "8", "9", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~", "!", "\"", "#", "$", "%",
            "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", ">", "=", "?", "@"]
```
We will hot-one encode the location in which the value was found. This can be either in the path, header or body of the request. Then we will assign the length of the value to the ```length``` field. In the ```lowercase``` and ```uppercase``` fields we will assign the amount of lower case and upper case alphabetical characters. The same goes for the remaining fields. The operation eventually creates a histogram for each value found in the request. These histograms are then stored to the hard drive as ```x_train.npy``` and ```x_test.npy``` so the machine learning model can learn from them.

### Model building
The neural network's architecture as discussed above is called an auto-encoder. This is because the network first encodes the original data into a lower dimension representation, before it decodes this lower representation into a close copy of the original. During training the error between the original and the decoded representation is used to adjust the neural weights accordingly. The implementation of this process is found in the [training script](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/class_training.py).

The neural network is relatively simple. The input layer consists of 48 neurons, representing the 48 fields contained by each histogram. The hidden layer consists of 4 neurons, which contain the latent space representation after compression. The output layer is the same size as the input layer and has 48 neurons. All layers are activated using the Rectified Linear Unit (ReLU) function.
```python
input_layer = layers.Input(shape=(48,))
encoded = layers.Dense(4, activation="relu")(input_layer)
decoded = layers.Dense(48, activation="relu")(encoded)

model = keras.Model(input_layer, decoded)
```
After the model is defined we must compile the model before we can start training. During this process we use the ```adam``` optimizer and use the Mean Squared Error (MSE) as our loss function. Other metrics we track are the Mean Squared Logarithmic Error (MSLE), Mean Absolute Error (MAE), Mean Absolute Percentage Error (MAPE) and the Cosine Similarity.
```python
model.compile(optimizer="adam", loss="mse", metrics=["mse", "msle", "mae", "mape", "cosine_similarity"])
```

Now it's time to train the model. We train the model based on the result of the input ```x_train``` and measure the loss based on the difference between the result and the original input ```x_train```. For our validation set we do the same thing but with the ```x_test``` data set. We train the entire data set 20 times, hence ```epochs=20``` and use a 64 batch size.
```python
model.fit(x_train, x_train, epochs=20, batch_size=64, validation_data=(x_test, x_test))
```

After training the MSE should look something like this:

![MSE training graph](https://raw.githubusercontent.com/Mathuiss/cyber_wolf/main/data/img/MSE.png)

The cosine simislarity should look something like this:

![Cosine Similarity training graph](https://raw.githubusercontent.com/Mathuiss/cyber_wolf/main/data/img/CosineSimilarity.png)


### Detection algorithm
Now that the model has been built we till take a look at the implementation in the [firewall](https://github.com/Mathuiss/cyber_wolf/blob/main/rel/cyberwolf.py). Firstly the model is loaded into memory using the ```load_model()``` function. When a connection is made and a request is sent by a client, this request will first be parsed by the preprocessor. This generates the features which our model can use. With the ```parse()``` function we can get the actual values from the request. Using the ```validate()``` function we can see which values are benign and which values are an anomaly.
```python
features = class_preprocessor.preprocess(msg)
values = class_validation.parse(msg)
class_validation.validate(model, values, features)
```

Taking a closer look at the validate function we can see that all values and features are first evaluated by our model. We generate a list of MSE's based on the request. Then we calculate the mean and the standard deviation of the MSE's. The flagging threshold is 1 standard deviation above the mean. The blocking threshold is set by multiplying an arbitrary epsilon value by the standard deviation and adding that to the standard deviation above the mean. The epsilon value can be set by a server administrator and can make the firewall more or less "sensitive". Lastly the detection threshold allows us to determine whether or not any cyber attack is present in the request. It is recommended to use the standard ```threshd=0.1``` value since this gives us the most accurate results. Next we loop through all values and if the MSE exceeds the ```threshb``` we will block the entire request. If the MSE only exceeds the flagging threshold, the value will be saved for manual review.
```python
list_mse = evaluate(model, values, features)

# Get the average MSE
mean = sum(list_mse) / len(list_mse)
# Get the standard deviation of the list
std_dev = np.std(list_mse)
# Get the flag threshold (mean + 1 * std dev)
threshf = mean + std_dev
# Get the block threshold (mean + 2 * std dev)
threshb = threshf + (epsilon * std_dev)

if std_dev <= threshd:
    return True

flags = []

for i in range(len(values)):
    if list_mse[i] >= threshb:
        return False

    if list_mse[i] >= threshf:
        flags.append(values[i])
        continue

append_flags(flags)

return True
```

If a request is dropped the TCPProxy will send the deny message and close the connection
```python
self.incoming_con.sendall(bytes("CONNECTION DENIED", "utf-8"))
tcp_proxy.incoming_con.close()
```

If a request is allowed the bytes will be sent to the web application and the response will be delivered to the caller.
```python
# Handle incoming connections
rec_msg = tcp_proxy.handle_incoming()

# If evaluation goes well, respond normally
if evaluate(model, rec_msg):
    # Proxy message to remote application
    proxy_response = tcp_proxy.handle_proxy(rec_msg)

    # Return response from remote to caller
    tcp_proxy.handle_response(proxy_response)
else:
    tcp_proxy.deny_connection()
```
