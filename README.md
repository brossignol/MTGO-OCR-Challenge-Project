# MTGO-OCR-Challenge-Project

This uses OCR to assist with data collection of MTGO challenges and other high stake events.  
Credit to Raptor56, PProteus, Zodiak, and Steb for working on the pauper data collection / coding over the years.  
Additional thank you to all of those who take the time to fill out the data sheets every week. Without you 
this project would not be possible.

## Important Information / Common Questions

  ### What is OCR?

   OCR stands for optimal character recognition or optimal character reader. It is the electronic or mechanical conversion 
   of images of typed, handwritten or printed text into machine-encoded text, whether from a scanned document, a photo 
   of a document, a scene-photo or from subtitle text superimposed on an image.
   
  ### What are we using it for?
  
  Collecting data from MTGO challenges is often a time consuming process. Inidivuals must keep the window open, and manually 
  type out the data. An example of what this looks like can be seen below.
 
   ![data](https://user-images.githubusercontent.com/82344270/141873248-74b5c1ec-40de-4e42-b7b4-516aa8a55b96.png)

  Typically, users will open an excel sheet, and copy this data by hand. This is incredibly tedious. This code automates
  this process by allowing users to upload an image (as seen above) and have our code return a CSV file of the text 
  using OCR. This speeds up the process dramatically, and allows more data to be collected. A visualization of this
  can be seen below.
  
  ![image](https://user-images.githubusercontent.com/82344270/141875261-3f64ba44-2aa1-44ea-9aad-4fe0572e8ee0.png)
 
  ### What Technology is used?
  OCR is a solved problem in the sense that there are a ton of tools that do this extremely well. It is highly 
  reccomended to use a prexisting library or service and adjust it to your needs. Options include Tesseract, 
  easyOCR, various products and services from companies like Amazon, Google, Microsoft, and much more. This
  project uses easyOCR. You can view their code here: https://github.com/JaidedAI/EasyOCR
 
### How does it work?

This code does the following:
- Take in an image.
- Modify the image using preprocessing techniques. (increase size, grayscale, threshold)
- Pass the image to easyOCR to generate a list of tuples containing the text from the image.
- Use an existing list of valid users to compare to the output and find possible matches. This acts as an autocorrect for ocr.
- Format the output to match the datasheet in csv formatting.
- Convert data to a csv file and return it.

# Example use case

Currently, this code is written to only work on standings. This ideally will help speed up collection for those who are  
collecting data right after an event. However, it is quite feasible to modify this to work on a full image later down the road.  
An example image is seen below.

![image](https://user-images.githubusercontent.com/82344270/154863220-5e9f4957-5fb5-495b-b389-5f0e3f6962ee.png)

An example use case of this bot is shown below.

![image](https://user-images.githubusercontent.com/82344270/154863495-8dac9277-dd93-48e4-84d3-7b73a1cfcc02.png)


## License
 
The MIT License (MIT)

Copyright (c) 2022 Raptor56

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.




