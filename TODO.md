### General
- [X] Switch to GTK4.0 from GTK3.0
  - [X] Refactor custom widgets for gtk4
  - [X] Perform regression testing

### Transaction Input Form
- [ ] Restrict amount input field to be numeric
- [X] Pass list of locations from data to form
- [X] Pass list of categories from data to form
- [ ] Connect transaction submission to data
- [X] Add completion to location and category dropdowns (https://docs.gtk.org/gtk3/class.EntryCompletion.html)
  

### Transaction List
- [X] Create TransactionList class to wrap functionality
  - [ ] Create method that returns a scrollable grid
    - [ ] Allow all fields to be edited
    - [ ] Allow deletion of transactions
    - [ ] Update in real-time when transactions are added to the list
  - [ ] Transaction writing function
    - [ ] Write data on a timer (every ~60 seconds)
    - [ ] Write data on application exit
  

### Account Balance Input Form
- [ ] TODO
  

### Dashboard
- [ ] TODO 
  

### Miscellaneous
- [ ] Change background color of app
- [ ] Research CSS for better look and feel