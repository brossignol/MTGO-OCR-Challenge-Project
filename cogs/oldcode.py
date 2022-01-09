# @commands.command(aliases=['Read'])
# async def read_standings(self, ctx, mtgo=None):

#     if mtgo == 'mtgo':
#         mtgo_data = True
#     else:
#         mtgo_data = False

#     """Takes in an image, reads it, and then spits out the csv."""
#     try:
#         image_url = ctx.message.attachments[0].url
#         if (image_url[0:26] == 'https://cdn.discordapp.com' and
#            image_url.endswith(('.jpg','.png','.jpeg'))):
#             await ctx.send(embed=discord.Embed(
#                 title=f"Success",
#                 description="Your image will be read. Please wait.",
#                 colour=discord.Color.blue()
#             ))
#             await ctx.message.attachments[0].save('image.png')
#             read_image(mtgo_data)
#             await ctx.send("I will now return your results.")
#             await ctx.send(file=discord.File('image-displayed.png'))
#             with open("output.csv", "rb") as file:
#                 await ctx.send("Here is your CSV file.", file=discord.File(file, "output.csv"))
#         else:
#             await ctx.send(discord.Embed(
#                 title=f"Error",
#                 description="The attachment provided was not an image.",
#                 colour=discord.Color.blue()
#             ))
#     except IndexError:
#         await ctx.send(embed = discord.Embed(
#             title=f"Error",
#             description="No image attached.",
#             colour=discord.Color.blue()
#         ))

# # Stores possible score readings that easyOCR might generate.
# score_readings = []
# for i in range (0, 15):
#     for j in range (0, 15):
#         score_readings.append(f'{i}{j}')
#         score_readings.append(f'{i}-{j}')
#     score_readings.append(f'{i}')

# # A dictionary to map bad score readings from easyOCR,
# # to good their correct counterpart. example: xy --> x-y
# correct_scores = {}
# for i in range (0, 15):
#     for j in range (0, 15):
#         correct_scores[f'{i}{j}'] = f'{i}-{j}'

# def cleanup(mtgo):
#     """removes image from system after reading."""
#     if mtgo:
#         os.remove('image-double.png')
#         os.remove('image-final.png')
#     os.remove('image.png')
#     os.remove('output.csv')

# def display_easyocr(results: list):
#     """This displays an image of what
#     easyocr was able to find by adding a green
#     rectangle around each word."""

#     img = cv2.imread(IMAGE_RESIZED)
#     for result in results:
#         top_left = tuple([int(result[0][0][0]), int(result[0][0][1])])
#         bottom_right = tuple([int(result[0][2][0]), int(result[0][2][1])])
#         img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
#     cv2.imwrite('image-displayed.png', img)


# def generate_csv(result: list, mtgo_data: bool):
#     """generates a csv file from the results that
#     easyOCR generated. This applies fine tuning to
#     mtgo data images. For anything else, it returns
#     what easyOCR found."""

#     print("generating csv")

#     if mtgo_data:
#         level = 0 # used to add newline when word moves down a row
#         with open("output.csv", "w") as file:
#             for reading in result:
#                 if reading[0][0][0] < level: # we are on a new line
#                     level = reading[0][0][0]
#                     file.write(f"\n{correct_easyOCR(reading[1], True)},")
#                 else:
#                     level = reading[0][0][0]
#                     file.write(f"{correct_easyOCR(reading[1], True)},")
#     else:
#         with open("output.csv", "w") as file:
#             for reading in result:
#                 file.write(f"{reading[1]},\n")


# def generate_standings_csv(result: list, mtgo_data: bool):
#     """generates a csv file for standings."""

#     print("generating csv")

#     if mtgo_data:
#         level = 0 # used to add newline when word moves down a row
#         with open("output.csv", "w") as file:
#             for reading in result:
#                 if reading[0][0][0] < level: # we are on a new line
#                     level = reading[0][0][0]
#                     file.write(f"\n{correct_easyOCR(reading[1], True)},")
#                 else:
#                     level = reading[0][0][0]
#                     file.write(f"{correct_easyOCR(reading[1], True)},")
#     else:
#         with open("output.csv", "w") as file:
#             for reading in result:
#                 file.write(f"{reading[1]},\n")

# def correct_easyOCR(reading: str, newline: bool):
#     """This fixes some common errors that easyOCR applies
#     to mtgo data and returns it as a corrected csv string.\n
#     These include:
#         - 21 instead of 2-1
#         - 'username 2-1' instead of 'username,2-1'"""

#     r = reading.split()
#     bad_string = False

#     if len(r) > 1:
#         for element in r:
#             if element in score_readings:
#                 bad_string = True
#     if not newline:
#         for i in range(len(r)):
#             if r[i] in correct_scores.keys():
#                 r[i] = correct_scores[r[i]]
#     if bad_string:
#         return ','.join(r)
#     else:
#         return ''.join(r)
