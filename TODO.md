### General (1/1)
- [X] Switch to GTK4.0 from GTK3.0
  - [X] Refactor custom widgets for gtk4
  - [X] Perform regression testing


### Transaction Input Form (4/5)
- [ ] Restrict amount input field to be numeric -- [Insert-Text Signal](https://docs.gtk.org/gtk4/signal.Editable.insert-text.html)
  - [ ] Look into making custom Entry widget
- [X] Pass list of locations from data to form
- [X] Pass list of categories from data to form
- [X] Connect transaction submission to data
- [X] Add completion to location and category dropdowns -- [Doc](https://docs.gtk.org/gtk3/class.EntryCompletion.html)
  

### Transaction List (3/6)
- [X] Create TransactionList class to wrap functionality
- [ ] Method that returns a scrollable grid 
  - [X] List transactions
  - [ ] Allow all fields to be edited
  - [ ] Button to delete transaction
  - [ ] Update in real-time when transactions are added to the list
    - [ ] Sort list according to transaction date (map/df of date->TransactionListItem?)
- [X] Transaction adding function
- [ ] Transaction deleting function
- [X] Transaction writing function
  - [X] Write data to file
  - [X] Write data on application exit
- [ ] Write transaction data to file on a timer (every ~60 seconds)
  

### Account Balance Input Form
- [ ] Create form to input account name, balance, and date
- [ ] Write account balance data to file
- [ ] Plot all account balances on same line graph
- [ ] Show table of balances (?)

### Dashboard
- [ ] TODO 
  

### Miscellaneous
- [ ] Change background color of app
- [ ] Research CSS for better look and feel