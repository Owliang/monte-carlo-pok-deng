I'm in Thailand and there is a gambling game and I want to know the best action for each situation. right now I'm thinking that I need to do the monte carlo simulation in python as the game is not well known. I want you to suggest that it's a good idea to do this or we can just do the math calculation

the game is called ป๊อกเด้ง in Thai
use 1 deck of card.
this game it's each player vs the house. not compete with each other


first, distribute 2 cards to all player randomly without showing to others

then each player need to calculate 2 things. points and "deng" which is เด้ง in Thai
- to calculate the point of their hand.
A is 1 point
2...9 are 2...9 point (equal to the face value)
T J Q K are 0 point
the point is the last digit of the number after you sum up all the cards.
ex. A Q = 1 point
2 7 is 9 points
5 5 is 0 point
- to calculate the deng of their hand.
deng is a multiplier of the payout of the bet.
if the suit of the 2 cards are the same then deng is 2 and the point calculate the same 
if your 2 cards are having the same value (e.g. 3 of heart and 3 of space) then it's 2 deng. and the point calculate the same (in this case it's 6)
else default deng is 1

** there are special rule to calculate deng at the end of the guide

continue

1st case ---- game ends immediately
if the house got pok kao or pok pad. the house and all the player must show their card immediately and resolve the game
we call 2 card with the points of 8 as "ป๊อกแปด" pok pad -> ป๊อก is pok and แปด is eight in Thai. (e.g. 26, 44, 99, K9)
we call 2 card with the points of 9 as "ป๊อกเก้า" pok kao -> ป๊อก is pok and เก้า is nine in Thai. (e.g. 27, A9, T9, 54)

pok kao is the highest hand in the game, beats everything
pok pad is the second highest hand in the same, beats everything except pok kao

here's how to resolve the game
- if a player has a point less than the house -> house wins the bet times the amount of deng that house has.
- if a player has a point equal to the house -> no pay to anyone
- if a player has a point more than the house -> player wins the bet times the amount of deng that player has

2nd case ---- house does not have pok kao or pok pad
if a player got pok kao or pok pad. that player need to show immediately and wait for the game to resolve. else continue playing

for each player that does not have pok kao or pok pad. they will have a chance to request for one more random card from the deck.
this time if after they get 1 more card and the points added up to 8 or 9. no need to show yet as it's not pok kao or pok pad because it has 3 cards


once all the player made a decision. the rest of the action is from the house. here's the list of action of the house (the house is still have only 2 cards at this point)

1. the house can simply open its hand and resolve the game for all player
2. the house can request for one more random card from the deck. then resolve the game for all player.
3. the house can resolve the game only with the player with 3 cards first. then choose to do either
    3.1 simply open its hand and resolve the game for the rest of the player with 2 cards
    3.2 request for one more random card from the deck. then resolve the game for the rest of the player with 2 cards


Special rule:
there is a special way to calculate the point and deng if the condition are met. these are only for 3 cards to encourage player to request for card.
1. 0.217% straight flush, basically it's in order and it all have the same suit like A23, 567, 9TJ, JQK. but QKA and KA2 won't count. then it's 5 deng, beat anything except pok kao or pok pad
2. 0.235% three of a kind (e.g. AAA, 333, KKK of any suites), then it's 5 deng, beat anything except pok kao or pok pad and the above in this list
3. 0.941% if your 3 cards are either J Q K, we call it three pictures, then it's 3 deng, beat anything except pok kao or pok pad and the above in this list
4. 3.26% straight, basically it's in order and it all not have the same suit like A23, 567, 9TJ, JQK. but QKA and KA2 won't count. then it's 3 deng, beat anything except pok kao or pok pad and the above in this list
5. 4.96% flush, your 3 cards are having the same suite, then it's 3 deng, beat anything except pok kao or pok pad and the above in this list