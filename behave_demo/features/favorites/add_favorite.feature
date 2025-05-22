Feature: Microsoft Edge Add Favorites
  As a Microsoft Edge user
  I want to add websites to my favorites
  So that I can quickly access them later

  Background:
    # Given I have launched Microsoft Edge browser
    # And I am on the new tab page

  Scenario: Add a website to favorites using the star icon
      When I navigate to "https://www.microsoft.com"
      And I click the star icon in the address bar
      And I click the "Done" button in the favorites dialog
      # Then "Microsoft" should appear in my favorites list
    
  Scenario: Add a website to favorites using keyboard shortcut
      When I navigate to "https://www.bing.com"
      And I press "Ctrl+D" on my keyboard
      And I click the "Done" button in the favorites dialog
      # Then "Bing" should appear in my favorites list

  Scenario: Add current page to favorites using address bar icon
    #   Given I launch Edge
      And I navigate to "https://www.microsoft.com"
      And I press "Ctrl+D" on my keyboard
      And the dialog should auto-fill the page name "Microsoft"
      And I should see "More", "Done" and "Remove" buttons

  Scenario: Test toggle favorites sorting
      And I click "Favorites" button
      And I click "Sort favorites" button
      And "Custom" should be toggled on
    
  # Scenario: Add a website to favorites with a custom name
  #   When I navigate to "https://www.github.com"
  #   And I click the star icon in the address bar
  #   And I change the name to "GitHub - Dev Platform"
  #   And I click the "Done" button in the favorites dialog
  #   Then "GitHub - Dev Platform" should appear in my favorites list
    
  # Scenario: Add a website to favorites in a specific folder
  #   When I navigate to "https://www.linkedin.com"
  #   And I click the star icon in the address bar
  #   And I select "Work" from the folder dropdown
  #   And I click the "Done" button in the favorites dialog
  #   Then "LinkedIn" should appear in the "Work" folder in my favorites list