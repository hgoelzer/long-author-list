# Long Author List 
Heiko Goelzer 2019 (h.goelzer@uu.nl)

Tool to edit long author lists and write formatted author names and affiliations

## Usage

### Run the program
python3 lal.py

Selected lines and selected blocks can be rearranged by dragging, sorted by last name and deleted.

'Save' will write the updated list to a file that can be reused later

'Parse' will write formatted output that can be copy-pasted 

### Input: lal_data2.txt 
Semicolon separated with one author per row and up to 5 affiliations

First;Last;Email;Group1;Group2;Group3;Group4;Group5 

Example: Heiko;Goelzer;h.goelzer@uu.nl;IMAU,UU;ULB;nil;nil;nil

Use 'nil','nan','0' or '-' to fill unused affiliations 

### Output: lal_inout2.txt 
When saving the modified listing, can be used as input the next time

### Parsed: lal_parsed_*.txt 
When parsed to insert in a manuscript


## Screen shot
![Alt text](/images/lal_screen.png?raw=true "Screen shot")
