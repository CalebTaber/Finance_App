### ~~General (1/1)~~
- [X] ~~Switch to GTK4.0 from GTK3.0~~
  - [X] ~~Refactor custom widgets for gtk4~~
  - [X] ~~Perform regression testing~~


### Transaction Input Form (4/7)
- [ ] Restrict amount input field to be numeric -- [Insert-Text Signal](https://docs.gtk.org/gtk4/signal.Editable.insert-text.html)
  - [ ] Look into making custom Entry widget
- [X] ~~Pass list of locations from data to form~~
- [X] ~~Pass list of categories from data to form~~
- [X] ~~Connect transaction submission to data~~
- [X] ~~Add completion to location and category dropdowns -- [Doc](https://docs.gtk.org/gtk3/class.EntryCompletion.html)~~
- [ ] Switch ComboBox to DropDown
- [ ] Switch ComboBoxText to DropDown
  

### Transaction List (4/4)
- [X] ~~Create TransactionList class to wrap functionality~~
- [X] ~~Method that returns a scrollable grid~~ 
  - [X] ~~List transactions~~
  - [X] ~~Allow all fields to be edited~~
  - [X] ~~Ability to delete transaction~~
  - [X] ~~Update in real-time when transactions are added to the list~~
    - [X] ~~Sort list according to transaction date (ListBox.set_sort_func())~~
- [X] ~~Transaction adding function~~
- [X] ~~Transaction writing function~~
  - [X] ~~Write data to file~~
  - [X] ~~Write data on application exit~~
  

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
- [ ] Write transaction data to file on a timer (every ~60 seconds)