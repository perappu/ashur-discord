#!/usr/bin/env python
# -*- coding: utf-8 -*- #
 
import random
from math import ceil
 
def buildFrequencyTable(text):
    """ Pair each word in the sample text with what word(s) are most likely to come after it. """

    # Turn the input text into a list of words/tokens
    sourceList = text.split()

    # Start our model as an empty dictionary
    markovModel = {}

    # Iterate through the sourceList to build our frequency table
    for i, word in enumerate(sourceList):

        # Check if we're at the end of the list
        if i+1 != len(sourceList):

            # If we haven't added this word to our table yet, add it
            if word not in markovModel:
                markovModel[word] = {sourceList[i+1]: 1}

            # If we have added this word to our table, record what word comes after it
            if word in markovModel:
                if sourceList[i+1] not in markovModel[word]:
                    markovModel[word][sourceList[i+1]] = 1

                else:
                    markovModel[word][sourceList[i+1]] += 1

        # If there is no following word
        else:
            markovModel[word] = {}

    return markovModel
    
def findNextWord(currentWord, markovModel):
    """ Use our frequency table to get the next word in sequence. """

    # If this line was
    if not markovModel[currentWord]:
        while not markovModel[currentWord]:
            currentWord = random.sample(markovModel.items(), 1)[0][0]

    potentialWords = []

    # For each potential next word's multiplicity, add it to the potentialWords list that many times
    # It's how we represent some words being more frequent than others
    for word in markovModel[currentWord]:
        for i in range(markovModel[currentWord][word]):
            potentialWords.append(word)

    # Pick something out of the potentialWords list to be our next word
    nextWord = random.choice(potentialWords)

    return nextWord
    
def makeASentence(text):
        
    output = ""
        
    markovModel = buildFrequencyTable(text)
    
    textLength = random.randint(2,10)
    
    word = random.sample(markovModel.items(), 1)[0][0]
    
    output = word + " "
    
    for i in range(textLength):
        word = findNextWord(word, markovModel)
        output += word + " "
        
    
    return output.strip()