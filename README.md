# Notice
  This project is outdated. You may consider [MTGO-log-parser](https://github.com/brossignol/MTGO-log-parser) before, which 
  retrives the same information based on the mtgo.exe logs. It is easier to use and doesn't have the OCR reading issues.

# MTGO-OCR-Challenge-Project
  This forked version implements reading of the standings. It was used for Vintage MTGO challenges parsing.
  More info at [MTGO Vintage Discord](https://discord.gg/2eVcsjK).
    
  This uses OCR to assist with data collection of MTGO challenges and other high stake events.  
  Credit to Raptor56, PProteus, Zodiak, and Steb for working on the pauper data collection / coding over the years.  
  Additional thank you to all of those who take the time to fill out the data sheets every week. Without you 
  this project would not be possible.

## Important Information / Common Questions

### What is OCR?
  OCR stands for optimal character recognition or optimal character reader. It is the electronic or mechanical conversion 
  of images of typed, handwritten or printed text into machine-encoded text, whether from a scanned document, a photo 
  of a document, a scene-photo or from subtitle text superimposed on an image.

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
  - Use an existing list of valid users to compare to the output and find possible matches.  
    This acts as an autocorrect for ocr.
  - Format the output to match the datasheet in csv formatting.
  - Convert data to a csv file and return it.

## Example use case
  Currently, this code is written to only work on standings. This ideally will help speed up collection for those who are collecting data right after an event. However, it is quite feasible to modify this to work on a full image later down the road. An example image is seen below.

![image](https://user-images.githubusercontent.com/82344270/166079889-b212033a-c2a2-4bf7-95b3-fd81fc79ee0a.png) ![image](https://user-images.githubusercontent.com/82344270/154863495-8dac9277-dd93-48e4-84d3-7b73a1cfcc02.png)

A video showing a demo and process of building this code / bot can be seen here: https://www.youtube.com/watch?v=a6f8ACJ9HmM


## Setup steps
  1. Clone the repository to your local machine. This repository uses pipenv to manage environments and dependencies. More information about pipenv and how to use it can be found here: https://realpython.com/pipenv-guide/

  2. Set up a bot using the Discord API. You can visit the discord developer portal for more information. Developer Portal Link: https://discord.com/developers/docs/intro
    
  3. You will need to create a credentials.json file for the google sheets API. A good tutorial on this topic can be seen here: https://www.youtube.com/watch?v=cnPlKLEGR7E. 

  4. This project uses a .env file to store sensitive information such as your discord bot token and google sheets urls. The following should be included in your .env file.

  - BOT_TOKEN=TOKEN_HERE
  - DOCS_LINK=FULL_LINK_HERE
  - GOOGLE_SHEET_URL_KEY=SHEET_KEY_HERE

  - Please note the following when setting the three env variables above
    - full link looks like this: docs.google.com/spreadsheets/d/KEY_HERE/edit?usp=sharing
    - key is the key the link above
  

  5. Finally, running 'python bot.py' should get your local instance up and running!

## License
 
The MIT License (MIT)

Copyright (c) 2023 Raptor56

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
