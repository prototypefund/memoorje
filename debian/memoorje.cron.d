# Check for pending capsule releases every three hours.
36 */3 * * *    root  /usr/bin/chronic /usr/bin/memoorjectl releasecapsules --no-color

# Send a message to the capsule owner once every tuesday, if one of the capsule recipients hasn't been verified yet.
57 2 * * 2      root  /usr/bin/chronic /usr/bin/memoorjectl sendcapsulehints --no-color

# Send notifications on journal changes every half hour.
*/30 * * * *    root  /usr/bin/chronic /usr/bin/memoorjectl sendjournalnotifications --no-color

# Check daily for pending notifications to trustees for capsules that are about to be released.
8 4 * * *    root  /usr/bin/chronic /usr/bin/memoorjectl sendpartialkeyinvitations --no-color

# Check daily for pending general reminders for capsule owners.
8 5 * * *    root  /usr/bin/chronic /usr/bin/memoorjectl sendreminders --no-color
