// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#include "dictionary.h"

// Represents number of children for each node in a trie
#define N 27

// Represents a node in a trie
typedef struct node
{
    bool is_word;
    struct node *children[N];
}
node;

// Represents a trie
node *root;

////global value for load and size counting the number of words of dictionary
int dicNum = 0;

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize trie
    root = malloc(sizeof(node));
    if (root == NULL)
    {
        return false;
    }
    root->is_word = false;
    for (int i = 0; i < N; i++)
    {
        root->children[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    ////create a pointer to track the TRIE
    node *mrTrack;

    // Insert words into trie
    while (fscanf(file, "%s", word) != EOF)
    {
        ////initialize the index for word[]
        int i = 0;

        ////let mrTrack point to the root
        mrTrack = root;

        ////dealing with one character each time until \0
        while (word[i])
        {
            int indexChildren;

            ////assign the character to a number
            if (word[i] == '\'')
            {
                indexChildren = N - 1;
            }
            else
            {
                indexChildren = word[i] - 'a';
            }

            ////check the content of children[word[i]]
            if (mrTrack->children[indexChildren] == NULL)
            {
                ////if null then allocate a new node and initialize memory
                mrTrack->children[indexChildren] = calloc(1, sizeof(node));
            }

            ////go to next node
            mrTrack = mrTrack->children[indexChildren];

            ////next chracter
            i++;
        }

        ////finish with this word and set its is_word to 1
        mrTrack->is_word = true;

        ////count the number of words in the dictionary
        dicNum++;
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return dicNum;
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    ////initialize the index of word[]
    int i = 0;
    ////set a pointer to track the trie
    node *trackCheck = root;

    ////iterate the character in the word
    while (word[i])
    {
        int indexChildren;

        ////lower an upper letter
        char c = tolower(word[i]);

        ////assign the character to a number
        if (c >= 'a' || c <= 'z')
        {
            indexChildren = c - 'a';
        }

        if (word[i] == '\'')
        {
            indexChildren = N - 1;
        }

        ////not even one word start with this character
        if (trackCheck->children[indexChildren] == NULL)
        {
            return false;
        }
        else
        {
            ////go to next node
            trackCheck = trackCheck->children[indexChildren];
        }

        ////next character
        i++;
    }

    ////check the status of is_word
    if (trackCheck->is_word)
    {
        return true;
    }

    ////is_word = 0, probably belongs to a path of some word else
    return false;
}

////recursive function helps to unload the allocated memory
int unloadRecursive(node *ptr)
{
    if (ptr == NULL)
    {
        //return;
        return 0;
    }

    for (int i = 0; i < 27; i++)
    {
        if (ptr->children[i] != NULL)
        {
            unloadRecursive(ptr->children[i]);
        }
    }

    ////if all 27 (including ') index are checked then free this node
    free(ptr);

    return 1;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    ////call the unloadRecursive function and get a return value 1 if succeed
    if (unloadRecursive(root))
    {
        return true;
    }
    else
    {
        return false;
    }
}