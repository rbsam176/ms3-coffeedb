| Page                     | Feature               | Expected behaviour                                                                                                              |
|--------------------------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------|
| Index                    | Down arrow            | Animates slightly up and down to gain attention of user                                                                         |
|                          | Nav                   | Becomes sticky after scrolling past initial title                                                                               |
|                          | Video                 | Plays 2 videos back-to-back in a loop, focus of video still visible when resizing                                               |
|                          | Search                | Entering search term takes user to Browse page with query actioned                                                              |
|                          |                       | Queries permitted: 'Brand' and 'Coffee name'                                                                                    |
|                          | Latest addition       | Shows most recent addition to the database                                                                                      |
|                          |                       | If no submissions, user not logged in, it displays message explaining no submissions have been added and invites them to signup |
|                          |                       | If no submissions, user logged in, it displays message explaining no submissions have been added and invites them to add        |
|                          | Top rated submissions | Shows 5 of the highest average ratings, their number of ratings and a link to the submission page                               |
|                          |                       | If no ratings, user logged in, it displays message explaining no submissions have been added and directs them to Browse page    |
|                          |                       | If no ratings, user not logged in, it displays message explaining no submissions have been added and invites them to login      |
|                          | Recent reviews        | Shows 3 most recent reviews, including the brand, name, review text, username and timestamp, with all links functional          |
|                          |                       | If no reviews, it displays message explaining no reviews have been added and directs them to Browse page                        |
|                          | Responsive layout     | All containers reposition themselves to vertically stack when on a smaller breakpoint                                           |
|                          |                       |                                                                                                                                 |
| Browse                   | Search                | Actions search query                                                                                                            |
|                          |                       | Queries permitted: 'Brand' and 'Coffee name'                                                                                    |
|                          | Open filter controls  | Clicking toggles state between 'Open filter controls' and 'Close filter controls' with corresponding arrow icon                 |
|                          | Filter: Roast         | Allows user to select multiple roast types                                                                                      |
|                          |                       | On clicking 'Search' the results returned only show results containing user 'roast' selection                                   |
|                          | Filter: Origin        | Allows user to select multiple origin types                                                                                     |
|                          |                       | On clicking 'Search' the results returned only show results containing user 'origin' selection                                  |
|                          |                       | Shows 4 of the most used 'origins' in the database                                                                              |
|                          |                       | If more than 4 'origins' exist in database, a 'down arrow button' is presented that reveals all 'origins'                       |
|                          | Filter: Organic       | Toggles between 2 states, Not Organic/Organic                                                                                   |
|                          |                       | On clicking 'Search' the results returned only show results that are organic                                                    |
|                          | Filter: Notes         | Toggling 'all' will only display submissions containing all of the user selected Notes                                          |
|                          |                       | Toggling 'any' will display any submissions containing any of the user selected Notes                                           |
|                          |                       | Only shows 10 notes by default                                                                                                  |
|                          |                       | All other notes are displayed when user clicks 'Show more' button                                                               |
|                          |                       | Font size of note is determined by its frequency in the database                                                                |
|                          | Filter validation     | Filter choices displayed above results with X button to remove individual parts of filter                                       |
|                          | Reset                 | Clicking reset removes any search query, goes back to default Browse view displaying all results                                |
|                          | Results header        | Changes text depending on whether the results are all or filtered                                                               |
|                          |                       | Contains bracketed number indicating how many results are shown                                                                 |
|                          | Sort dropdown         | Allows user to sort results by Recent > Old, Old > Recent, Name A-Z, Name Z-A, Brand A-Z, Brand Z-A                             |
|                          | Pagination            | Displays page number out of number of pages and results X to 6                                                                  |
|                          |                       | Provides previous and next buttons both above and below results                                                                 |
|                          |                       | Buttons become disabled if there is no next/previous page                                                                       |
|                          |                       | Buttons aren't visible if results fit on one page                                                                               |
|                          | Submission card       | Displays average rating in top left, if rating exists                                                                           |
|                          |                       | Displays EDIT button in top right, if user is logged in and is owner of submission being viewed                                 |
|                          |                       | Displays image decoded from Base64                                                                                              |
|                          |                       | Clicking image takes user to 'View Submission' page                                                                             |
|                          |                       | Displays Roast, Origin, whether submission is organic, 'More Info' link to roaster website, flavour notes                       |
|                          |                       | Clicking flavour notes takes user to Browse page with clicked note as filter criteria                                           |
|                          |                       | Displays username of user that made the submission, links to their profile which displays all of their submissions              |
|                          |                       |                                                                                                                                 |
| Add/Edit                 |                       | Only shows if user is logged in                                                                                                 |
|                          |                       | On desktop, left half is input fields, right half is live preview                                                               |
|                          |                       | Live preview updates with every change user makes to input fields                                                               |
|                          |                       | All fields required except Website (and image if on Edit endpoint)                                                              |
|                          |                       | Image submitted gets encoded into base64 and submitted to database                                                              |
|                          |                       | After image file uploaded, file input label changes to validate user action                                                     |
|                          |                       | Only image files permitted to be selected                                                                                       |
|                          |                       | Selecting 'Other...' on Brand and Origin selection presents user with custom text input field                                   |
|                          |                       | Custom Brand and Origin text input fields presents autocomplete suggestions if pre-existing values to prevent duplicates        |
|                          |                       | Only 4 flavour notes permitted, notes should become disabled when 4th is clicked                                                |
|                          |                       | If 4 notes are selected, 'un-checking' one should release the disabled state                                                    |
|                          |                       | Only 10 notes should be visible by default                                                                                      |
|                          |                       | 'Show all X notes' X should be dynamic, representing number of unique notes in database                                         |
|                          |                       | Add button on custom note text input is disabled until text is typed in                                                         |
|                          |                       | Custom note text input presents autocomplete suggestions if pre-existing values to prevent duplicates                           |
|                          |                       | If 3 notes are selected and the user enters a custom note then all notes become disabled                                        |
|                          |                       | Hitting 'enter' key on keyboard submits custom note, does not submit form                                                       |
|                          |                       | Custom notes appear below 'Show more'/'Show less' button                                                                        |
|                          |                       | 'Submit' button submits all data to database                                                                                    |
|                          |                       | After submitting, user is taken to 'View Submission' page with flash message validating user action                             |
|                          |                       | If user is on Edit endpoint, text input values are pre-filled with submission data                                              |
|                          |                       | Edit endpoint shows Delete submission option, clicking it triggers a second button to click                                     |
|                          |                       |                                                                                                                                 |
| Profile (default view)   |                       | First name of user is displayed, member since date and number of submissions                                                    |
|                          |                       | Default view of profile shows all user submissions                                                                              |
|                          |                       | If no submissions exist and user is logged in, message is displayed with link to Add                                            |
|                          |                       | If no submissions exist and another user viewing is logged in, message is displayed with link to homepage                       |
|                          |                       | Pagination exists if user has more than 6 submissions                                                                           |
|                          |                       |                                                                                                                                 |
| Profile (update account) |                       | User is able to change first name, last name, email and username without having to enter password                               |
|                          |                       | Changing user information refreshes page with flash message validating user action                                              |
|                          |                       | User must enter existing password to change it to something new                                                                 |
|                          |                       | Change password button is disabled unless at least 8 characters have been entered into 'Existing password' field                |
|                          |                       | All password fields are required                                                                                                |
|                          |                       | Password criteria shows 'filled' icon when each criteria has been met                                                           |
|                          |                       | Changing user password refreshes page with flash message validating user action                                                 |
|                          |                       |                                                                                                                                 |
| Profile (delete account) |                       | User must enter their username and password before 'Delete my account permanently' button becomes active                        |
|                          |                       | Clicking 'Delete my account permanently' button displays a second 'Permanently Delete' button                                   |
|                          |                       | Clicking 'Permanently Delete' button actions the removal of user account from database                                          |
|                          |                       | Deleting user account also deletes all submissions submitted by that user                                                       |
|                          |                       | Incorrect username/password flash message validation appears                                                                    |
|                          |                       |                                                                                                                                 |
| Logout                   |                       | Clicking logout takes user to login page with flash message validating user action                                              |
|                          |                       |                                                                                                                                 |
| Login                    |                       | Email and password fields required                                                                                              |
|                          |                       | Displays link to signup if user hasn't an account already                                                                       |
|                          |                       | Clicking 'login' logs user in if information is correct                                                                         |
|                          |                       |                                                                                                                                 |
| View Submission          |                       | If user not logged in, review text input and submit button are disabled                                                         |
|                          |                       | If user not logged in, clicking on star rating displays flash message with link to login                                        |
|                          |                       | If user is logged in, clicking on star rating updates to reflect user rating and updates average rating accordingly             |
|                          |                       | If user is logged in and user has already reviewed submissions, review text input box contains user review                      |
|                          |                       | If user is logged in and user has already reviewed submissions, submitting review updates pre-existing review                   |
|                          |                       | If user is logged in and has not reviewed submission, review text input has placeholder and submit actions adding to database   |
|                          |                       | Review text input is limited to 150 characters                                                                                  |
|                          |                       | As user is typing, character count below text input box updates accordingly                                                     |
|                          |                       | If user already has a review submitted, the character count on page load already adjusts to pre-existing review                 |
|                          |                       | 'Write a review' / 'Edit your review' header depending on if user already has review submitted                                  |
|                          |                       | If more than 3 reviews exist, 'See all reviews' button becomes visible                                                          |
|                          |                       | 3 reviews visible on page only                                                                                                  |
|                          |                       | Review shows user rating if it exists                                                                                           |
|                          |                       | User's own review is highlighted yellow                                                                                         |
|                          |                       | Hovering over rating icons will highlight all icons left of hovered icon                                                        |
|                          |                       |                                                                                                                                 |
| All Reviews              |                       | User's own review is highlighted yellow                                                                                         |
|                          |                       | Sortable by date (recent and old) and rating (high > low and low > high)                                                        |
|                          |                       | User ratings displayed                                                                                                          |
|                          |                       | Back button displayed in top left corner                                                                                        |
|                          |                       |                                                                                                                                 |
| Signup                   |                       | All fields required                                                                                                             |
|                          |                       | Password criteria shows 'filled' icon when each criteria has been met                                                           |
|                          |                       | Displays link to login if user already has an account                                                                           |
|                          |                       | Clicking 'Sign Up' actions request and adds user to database                                                                    |
|                          |                       | After signing up, user is redirected to profile page with flash message validating action                                       |
|                          |                       | User is prevented from signing up with already-existing email or username                                                       |
|                          |                       | After entering first and last name, the username text input value is pre-filled with suggested username                         |
|                          |                       |                                                                                                                                 |
| 404 Error                |                       | Presented if user go to non-existing endpoint                                                                                   |
|                          |                       |                                                                                                                                 |
| None-page-specific       |                       | If user goes to page that requires being logged in, and are not logged in, they are redirected to another page                  |