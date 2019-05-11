# LongAuthorList formatting tool
# Heiko Goelzer (h.goelzer@uu.nl 2019)

# Expect lal_data.txt with one author per row and up to 5 affiliations
# <First>; <Last>; <Group1>; <Group2>; <Group3>; <Group4>; <Group5> 
# Example: Heiko; Goelzer; IMAU,UU; ULB; nil; nil; nil

import tkinter as tk;

# Listbox for ordering
class ReorderableListbox(tk.Listbox):
    """ A Tkinter listbox with drag & drop reordering of lines """
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.EXTENDED
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<Control-1>', self.toggleSelection)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.bind('<Leave>',  self.onLeave)
        self.bind('<Enter>',  self.onEnter)
        self.selectionClicked = False
        self.left = False
        self.unlockShifting()
        self.ctrlClicked = False
    def orderChangedEventHandler(self):
        pass

    def onLeave(self, event):
        # prevents changing selection when dragging
        # already selected items beyond the edge of the listbox
        if self.selectionClicked:
            self.left = True
            return 'break'
    def onEnter(self, event):
        #TODO
        self.left = False

    def setCurrent(self, event):
        self.ctrlClicked = False
        i = self.nearest(event.y)
        self.selectionClicked = self.selection_includes(i)
        if (self.selectionClicked):
            return 'break'

    def toggleSelection(self, event):
        self.ctrlClicked = True

    def moveElement(self, source, target):
        if not self.ctrlClicked:
            element = self.get(source)
            self.delete(source)
            self.insert(target, element)

    def unlockShifting(self):
        self.shifting = False
    def lockShifting(self):
        # prevent moving processes from disturbing each other
        # and prevent scrolling too fast
        # when dragged to the top/bottom of visible area
        self.shifting = True

    def shiftSelection(self, event):
        if self.ctrlClicked:
            return
        selection = self.curselection()
        if not self.selectionClicked or len(selection) == 0:
            return

        selectionRange = range(min(selection), max(selection))
        currentIndex = self.nearest(event.y)

        if self.shifting:
            return 'break'

        lineHeight = 12
        bottomY = self.winfo_height()
        if event.y >= bottomY - lineHeight:
            self.lockShifting()
            self.see(self.nearest(bottomY - lineHeight) + 1)
            self.master.after(500, self.unlockShifting)
        if event.y <= lineHeight:
            self.lockShifting()
            self.see(self.nearest(lineHeight) - 1)
            self.master.after(500, self.unlockShifting)

        if currentIndex < min(selection):
            self.lockShifting()
            notInSelectionIndex = 0
            for i in selectionRange[::-1]:
                if not self.selection_includes(i):
                    self.moveElement(i, max(selection)-notInSelectionIndex)
                    notInSelectionIndex += 1
            currentIndex = min(selection)-1
            self.moveElement(currentIndex, currentIndex + len(selection))
            self.orderChangedEventHandler()
        elif currentIndex > max(selection):
            self.lockShifting()
            notInSelectionIndex = 0
            for i in selectionRange:
                if not self.selection_includes(i):
                    self.moveElement(i, min(selection)+notInSelectionIndex)
                    notInSelectionIndex += 1
            currentIndex = max(selection)+1
            self.moveElement(currentIndex, currentIndex - len(selection))
            self.orderChangedEventHandler()
        self.unlockShifting()
        return 'break'

    def deleteSelection(self):
        # delete selected items 
        if len(self.curselection()) == 0:
            return
        self.delete(min(self.curselection()),max(self.curselection()))

    def sortAll(self):
        # sort all items alphabetically
        temp_list = list(self.get(0, tk.END))
        temp_list.sort(key=str.lower)
        # delete contents of present listbox
        self.delete(0, tk.END)
        # load listbox with sorted data
        for item in temp_list:
            self.insert(tk.END, item)

    def sortSelection(self):
        # sort selected items alphabetically
        if len(self.curselection()) == 0:
            return
        mmax = max(self.curselection())
        mmin = min(self.curselection())
        temp_list = list(self.get(mmin,mmax))
        #print(temp_list)
        # Sort reverse because pushed back in reverse order
        temp_list.sort(key=str.lower,reverse=True)
        # delete contents of present listbox
        self.delete(mmin,mmax)
        # load listbox with sorted data
        for item in temp_list:
            self.insert(mmin, item)

    def save(self,df):
        # save current list
        temp_list = list(self.get(0, tk.END))
        # create output df
        dfout = pd.DataFrame()
        for item in temp_list:
            items = item.split(",")
#            print(items[3])
            matchl = (df["LastName"].isin([items[0]]))
            matchf = (df["FirstName"].isin([items[1]]))
#            print(df[matchi])
            dfout = dfout.append(df[matchf & matchl])
        print(dfout)
        dfout.to_csv('lal_inout.txt', sep=';', header=None, index=None)
        print("File written!")

    def parse(self,df):
        # save current list
        temp_list = list(self.get(0, tk.END))
        # create output df
        dfout = pd.DataFrame()
        for item in temp_list:
            items = item.split(",")
            matchl = (df["LastName"].isin([items[0]]))
            matchf = (df["FirstName"].isin([items[1]]))
            dfout = dfout.append(df[matchf & matchl])
        # parse 
        first = dfout["FirstName"]
        last = dfout["LastName"]
        grp1 = dfout["Group1"]
        grp = dfout[["Group1","Group2","Group3","Group4","Group5"]]
        unique_groups = []
        group_ids = []
        k = 0
        # collect unique groups and indicies
        for i in range(0,dfout.shape[0]):
            #print(unique_groups, len(unique_groups))
            if grp1.iloc[i] not in unique_groups:
                #print(i,unique_groups)
                unique_groups.append(grp1.iloc[i])
                k = k + 1
                group_ids.append(k)
            else:
                ix = unique_groups.index(grp1.iloc[i])
                group_ids.append(ix)

        # Compose text
        with open("lal_parsed.txt", "w") as text_file:
            # write out names
            for i in range(0,dfout.shape[0]): 
                print(first.iloc[i].strip(), end =" ", file=text_file)
                print(last.iloc[i].strip(), end ="", file=text_file)
                print(str(group_ids[i]), end =" ", file=text_file)
                print(",", end ="", file=text_file)
            # between names and affiliations    
            print("\n\n", file=text_file)
            # write out affiliations
            for i in range(0,len(unique_groups)): 
                print("(", end ="", file=text_file)
                print(str(group_ids[i]), end ="", file=text_file)
                print(")", end ="", file=text_file)
                #print(group_ids[i], len(unique_groups), unique_groups[group_ids[i]])
                print(unique_groups[group_ids[i]], end ="\n", file=text_file)
        print("\n File parsed!")
        
        
# Main program
import pandas as pd
import numpy as np

# Read input data from file
#df = pd.read_csv('test.csv', sep=',', low_memory=False, encoding='iso8859_15')
df = pd.read_csv('lal_data.txt', sep=';', header=None ,names=np.array(['FirstName', 'LastName', 'Group1','Group2','Group3','Group4','Group5']))
#print(df)
#print(df.size)
#print(df.shape[0])

# Start GUI to sort names
root = tk.Tk()
root.geometry("200x800") 
#root.resizable(0, 0) 

listbox = ReorderableListbox(root)
for i in range(0,df.shape[0]): 
    listbox.insert(tk.END, df.at[i,'LastName'] + ',' + df.at[i,'FirstName'] +
                   ',' + str(i) )

listbox.pack(fill=tk.BOTH, expand=True)

# Add a delete button
db = tk.Button(root, text="Delete", height=2, 
               command=lambda listbox=listbox: listbox.deleteSelection())
db.pack(fill=tk.BOTH, expand=False)

# Add button to sort all entries
sortallb = tk.Button(root, text="Sort All", height=2, command = lambda: listbox.sortAll())
sortallb.pack(fill=tk.BOTH, expand=False)

# Add button to sort the selection
sortb = tk.Button(root, text="Sort Selection", height=2, command = lambda: listbox.sortSelection())
sortb.pack(fill=tk.BOTH, expand=False)

# Add a save button
saveb = tk.Button(root, text="Save", height=2, command = lambda: listbox.save(df))
saveb.pack(fill=tk.BOTH, expand=False)

# Add a save button
parseb = tk.Button(root, text="Parse", height=2, command = lambda: listbox.parse(df))
parseb.pack(fill=tk.BOTH, expand=False)


# Run the tk window
root.mainloop()

