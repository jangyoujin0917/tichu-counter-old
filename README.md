# tichu-counter
Tichu score counter using Pygame.

## Commands in GUI line
### force \<red score> \<blue score>
Force the score of this round to input values. Tichu claim is ignored.
### lt \<claim|success|fail> \<player no.>
Commands about large tichu.
### st \<claim|success|fail> \<player no.>
Commands about small tichu.
### score \<red score> \<blue score>
Input the score of this round and end the round. After this command, large/small tichu score and the score of the card value is reflected to total score.
### onetwo \<red|blue>
End this round with onetwo. No card scores are needed, but large/small tichu is reflected to total score.
### undo
Undo the commands. (except undo, end, quit)
### end
Save the data with txt files.
### quit
Close the window. 'end' command is executed automatically.
