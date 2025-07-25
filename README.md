<p align="center">
  <img src="docs/images/logo_2.png" alt="BookBase logo" width="150">
</p>

# 📚 BookBase

### Your personal Book Collection Tracker

## Project Overview

**BookBase** is a full-stack **Book Collection Tracker** that allows users to create and manage their own digital book collection.
It is designed for book enthusiasts who want an easy way to track their reading, organize books by category, and store notes or impressions for each title.

The initial version focuses on a single admin user who can:

- Add, edit, delete, and view books
- Track read/unread status
- View basic book information such as title, author, genre, and description
- Optionally retrieve book data (title, cover, description) from the Google Books API

## 👥 Target Audience

BookBase is designed for:

- **Book collectors and readers** who want a personal library management tool
- **Students or researchers** tracking their reading across subjects or disciplines
- **Aspiring writers** who keep reading logs and references
- **Casual readers** who want to mark books as read/unread and leave private notes
- (In future versions) **Registered users** who want to share and comment on public book lists

Visitors to the site can:

- Browse public book collections
- Search for books using a built-in interface _(planned)_
- View book details, but cannot modify or comment

## 🔮 Future Features

BookBase is designed to evolve. Planned enhancements include:

- User registration and individual collections
- Role-based permissions (e.g., moderators, admins)
- Public/private toggle for each user’s collection
- Commenting on public book entries _(for registered users only)_
- Google Books search integration
- Cover image and metadata auto-fill

---

**BookBase** is built with **Django**, uses a **relational database**, and follows best practices for UX, accessibility, and secure deployment. It is designed to be simple to use and easy to expand.

---

## 🧩 User Stories

Each story is grouped and labelled by priority:  
**Must-have**, **Should-have**, and **Could-have** based on MS3 criteria and the planned scope of BookBase.

---

### ✅ Must-Have Features

#### 🟦 1. Add New Book to Collection

As an admin user I want to add a new book to my collection so that I can track what I’m reading

**Acceptance Criteria:**

- **Given** I am on the "Add Book" page
- **When** I submit a form with book data
- **Then** the new book appears in my collection

**Tasks:**

- Create `Book` model
- Create Django form and view for adding books
- Add success/failure feedback messages  
  **Label:** `Must-have`

---

#### 🟦 2. View Book Collection

As a site visitor I want to view the public book collection so that I can explore books added by the admin

**Acceptance Criteria:**

- **Given** I visit the homepage or browse page
- **When** I load the page
- **Then** I see a list of public books with basic info

**Tasks:**

- Build book list view
- Filter only public books
- Add Bootstrap card/grid layout  
  **Label:** `Must-have`

---

#### 🟦 3. Edit or Delete a Book (Admin)

As an admin user I want to edit or delete books so that I can keep the collection accurate

**Acceptance Criteria:**

- **Given** I’m logged in and own the book
- **When** I click "Edit" or "Delete"
- **Then** the book is updated or removed

**Tasks:**

- Add `edit` and `delete` views and templates
- Add edit/delete buttons
- Restrict actions to admin only  
  **Label:** `Must-have`

---

#### 🟦 4. Mark Book as Read/Unread

As a user I want to mark a book as "read" or "unread" so that I can track my progress

**Acceptance Criteria:**

- **Given** a book entry is displayed
- **When** I click the "Read" toggle
- **Then** its status updates accordingly

**Tasks:**

- Add `is_read` boolean to model
- Add toggle button in template
- Style accordingly  
  **Label:** `Must-have`

---

### ✅ Should-Have Features

#### 🟧 5. Google Books API Integration

As an admin I want to auto-fill book details sSo that I don’t need to enter them manually

**Acceptance Criteria:**

- **Given** I search by title or ISBN
- **When** I click "Fetch Info"
- **Then** form fields are pre-filled with book data

**Tasks:**

- Integrate Google Books API
- Create fetch function + form autofill
- Add fallback if no results  
  **Label:** `Should-have`

---

#### 🟧 6. Public/Private Collection Toggle

As a user I want to choose if my collection is public So that I can control visibility

**Acceptance Criteria:**

- **Given** I’m editing my profile
- **When** I toggle visibility
- **Then** my book list appears/disappears for guests

**Tasks:**

- Add `is_public` to user profile
- Filter collection views accordingly  
  **Label:** `Should-have`

---

### ✅ Could-Have Features

#### 🟨 7. Comment on Public Books

As a registered user I want to comment on public books so that I can leave thoughts or recommendations

**Acceptance Criteria:**

- **Given** I’m logged in and viewing a book
- **When** I submit a comment
- **Then** it appears below the book

**Tasks:**

- Create `Comment` model and form
- Restrict to logged-in users
- Display comments with timestamps  
  **Label:** `Could-have`

---

#### 🟨 8. User Avatar Upload

As a user I want to upload a profile picture So that I can personalize my account

**Acceptance Criteria:**

- **Given** I’m editing my profile
- **When** I upload an image
- **Then** it appears next to my name or comments

**Tasks:**

- Add `ImageField` to user profile
- Add Cloudinary (or skip in MVP)
- Display avatar in UI  
  **Label:** `Could-have`

## 📊 Entity Relationship Diagram (ERD)

The following diagram shows the core data model for **BookBase**:

- **User**  
  Represents a registered user.

- **Book**  
  Stores book data fetched from the Google Books API or manually entered _(planned feature)_.

- **UserBook**  
  Connects users to books they've added to their personal collection.

- **Note**  
  Allows users to attach private notes to books in their collection.

- **Comment** _(future feature)_  
  Enables users to leave public comments on books.

> 💡 _If a book is not found via Google Books, future versions may allow manual entry including cover uploads._

![BookBase ERD](docs/erd/bookbase_erd.png)

## This structure supports all core CRUD operations and prepares the project for future features such as user accounts and comment management.

## 🧩 Wireframes

The following wireframes represent the planned layout and structure of key pages across **desktop**, **tablet**, and **mobile** views for the BookBase application.

> ⚠️ **Note:** These wireframes are conceptual. Visual appearance, element placement, or features may change based on testing and user feedback during development.

### 🏠 Home Page (index.html)

![BookBase Home Wireframe - Desktop/Tablet/Mobile](docs/wireframes/Index.png)

### ℹ️ About Page

![BookBase About Wireframe - Desktop/Tablet/Mobile](docs/wireframes/About.png)

### 📚 My Collection Page

![BookBase Collection Wireframe - Desktop/Tablet/Mobile](docs/wireframes/Collection.png)

### 👤 Profile Page

![BookBase Profile Wireframe - Desktop/Tablet/Mobile](docs/wireframes/Profile.png)

---

## Project Setup & Milestones

This section outlines the key setup steps and development milestones completed during the BookBase project:

1. ✅ Created project folder and initialized a Git repository
2. ✅ Set up Python virtual environment and installed Django
3. ✅ Created Django project (`bookbase`) and initial app (`books`)
4. ✅ Registered `books` app in `settings.py`
5. ✅ Implemented user authentication system (register, login, logout)
6. ✅ Set login/logout redirect URLs using `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL`
7. ✅ Created shared `base.html` layout with navigation and footer
8. ✅ Built views and templates for:
   - Home
   - About Us
   - My Collection
   - Profile
9. ✅ Configured conditional navbar logic using `{% if user.is_authenticated %}`
10. ✅ Handled common issues (NoReverseMatch, logout 405 error, login redirect to `/accounts/profile/`)
11. ✅ Created custom logout view to allow GET requests for logout link
12. ✅ Verified full user flow from registration → login → logout
13. ✅ Created Book model and linked books to the currently logged-in user
14. ✅ Built Add Book form with fields for title, author, description, cover URL, status, and notes
15. ✅ Displayed added books on My Collection page, styled with Bootstrap
16. ✅ Rendered optional notes beneath each book entry
17. ✅ Improved social links layout in footer and addressed visual inconsistencies
18. ✅ Centered book collection cards and used badges for book status
19. ✅ Added Edit and Delete functionality for books with route-based permissions
20. ✅ Implemented edit_book view using pre-filled Django ModelForm and styled form template
21. ✅ Created delete_book view with confirmation step using POST form
22. ✅ Secured all book actions using @login_required and ownership filtering (book.user == request.user)
23. ✅ Verified form behavior, redirect flow, and error handling for invalid book IDs
24. ✅ Applied conditional badge styling (e.g. red for “Un-read”) based on book status
25. ✅ Integrated Google Books API for autofill in Add Book form
26. ✅ Allowed both Enter key and Search button to trigger API request
27. ✅ Displayed results in responsive Bootstrap cards with "Use this" autofill buttons
28. ✅ Handled edge cases (missing author, long descriptions, broken cover links)
29. ✅ Improved JavaScript handling for JSON encoding and character safety
30. ✅ Created /get_books/ API endpoint to fetch books from Google Books dynamically
31. ✅ Built JavaScript logic to render responsive book cards on the homepage using live API data
32. ✅ Adjusted homepage layout to remove static cards and support dynamic injection
33. ✅ Added {% block scripts %} support in base.html for page-specific JavaScript
34. ✅ Ensured proper responsive scaling of cards (200–300px wide, 300–400px tall) using Bootstrap
35. ✅ Confirmed real-time data loading and rendering without page refresh
36. ✅ Integrated Google Books cards grid on homepage with:
    - Title, author, thumbnail, and collapsible description
    - Responsive layout with Bootstrap columns
    - Cards sized 200–300px wide and 300–400px tall
37. ✅ Implemented search, genre filter, and sort dropdowns (by relevance/newest)
38. ✅ Added "Load More" button with 24-book pagination per batch
39. ✅ Designed consistent and collapsible "More" section for book descriptions
40. ✅ Styled and centered Discover Books heading and controls
41. ✅ Made Load More button visible and styled with hover/fade states
42. ✅ Ensured placeholder image loads if book thumbnail fails
43. ✅ Confirmed full dynamic rendering via AJAX without page reloads
44. ✅ Created global style.css and served it using Django STATICFILES_DIRS
45. ✅ Fixed layout misalignments (genre/sort spacing, button overflow, column drop)
46. ✅ Implemented search, genre filter, and sort dropdowns (by relevance/newest)
47. ✅ Added "Load More" button with 24-book pagination per batch
48. ✅ Designed consistent and collapsible "More" section for book descriptions
49. ✅ Styled and centered Discover Books heading and controls
50. ✅ Made Load More button visible and styled with hover/fade states
51. ✅ Ensured placeholder image loads if book thumbnail fails
52. ✅ Confirmed full dynamic rendering via AJAX without page reloads
53. ✅ Created global style.css and served it using Django STATICFILES_DIRS
54. ✅ Fixed layout misalignments (genre/sort spacing, button overflow, column drop)
55. ✅ Created responsive About page with background and card styling
56. ✅ Built Profile page with avatar fallback, editable bio, and reading stats
57. ✅ Refactored bio edit form to appear inline on toggle (JS-enabled)
58. ✅ Applied consistent background color across key cards (#acbdd8)
59. ✅ Improved profile layout, adjusted spacing inside the profile card using Bootstrap utility classes
60. ✅ Enabled inline editing of username/email, created UserUpdateForm to edit Django User fields
61. ✅ Enhanced profile stats section, rearranged display: Total books → Unread → Read
62. ✅ Made footer sticky on large screens, updated base.html layout with d-flex flex-column min-vh-100
63. ✅ Added auto-delete for old avatar images, if a new avatar is uploaded, the old image file is removed from /media/avatars/
64. ✅ Protected default avatar image, ensured placeholder avatar (avatar-placeholder.png) is not deleted during updates
65. ✅ Enabled avatar compression and resizing, resizes uploaded avatars to a maximum of 300x300 pixels
66. ✅ Preserved bio during avatar upload, prevented bio text from disappearing by passing it as a hidden field in the avatar form
67. ✅ Applied 2:3 aspect ratio to My Collection book covers using Bootstrap ratio utility
68. ✅ Standardized image layout with object-fit: contain and fallback placeholder for missing covers
69. ✅ Matched Add Book search results layout with consistent card styling and image sizing
70. ✅ Made navbar fixed-top and right-aligned navigation links for improved accessibility
71. ✅ Centered tagline ("Your personal book collection tracker.") in the navbar on desktop view
72. ✅ Prevented navbar-title overlap on tablets by adjusting layout responsiveness and spacing


---

## Troubleshooting & Known Fixes

While developing BookBase, several key issues were encountered and resolved:

- **Login redirected to `/accounts/profile/` instead of homepage**  
  _Cause:_ Django's `LoginView` defaults to `/accounts/profile/`  
  _Fix:_ Added `LOGIN_REDIRECT_URL = 'home'` to `settings.py`

- **Logout returned HTTP 405 error**  
  _Cause:_ Logout was triggered via a `GET` request; Django expects `POST`  
  _Fix:_ Replaced direct `<a>` logout link with a form using `POST` method

- **`NoReverseMatch` errors for views like `home`, `about`, `profile`**  
  _Cause:_ View names used in `base.html` didn't exist yet  
  _Fix:_ Created placeholder views in `views.py` and linked them in `urls.py`

- **Cover image URL caused validation or 502 error**
  Cause: Using right-click → "Copy image address" from Google Images often gives base64 or unusable proxies
  Fix: Used clean direct image URLs (e.g. from OpenLibrary or Goodreads cover images)

- **Social links in footer showed unexpected \_ character**
  Cause: Font Awesome misrendering or extra whitespace - still not solved, left for later
  Fix: Tweaked <i> tags and surrounding layout with spacing classes (gap-3, align-items-center, etc.)

- **Footer elements not aligned**
  Cause: Text and icons stacked vertically by default
  Fix: Used Bootstrap's flex utilities to align items side-by-side and justify space between

- **Pressing Enter in search field refreshed page instead of triggering search**  
  _Cause:_ Default form submission behavior not prevented  
  _Fix:_ Added `event.preventDefault()` in `searchBooks(event)` function

- **Some Google Books entries didn't autofill form fields**  
  _Cause:_ JSON.stringify created invalid JavaScript when special characters (e.g., `'`) present  
  _Fix:_ Moved book data into `data-book` attribute and safely parsed with `JSON.parse()` inside `fillFormFromElement()`

- **Form fields remained blank for some Google Books entries**  
  _Cause:_ Some API entries were missing author, description, or cover  
  _Fix:_ Defaulted to empty strings using fallback logic like `book.cover_url || ''`

- **Runserver crashed with 'views has no attribute' error**  
  _Cause:_ `search_google_books` view was not properly imported or declared  
  _Fix:_ Verified view was defined in `views.py` and matched exactly in `urls.py`

- **Dynamic homepage showed only static cards**
  _Cause:_ Old test cards were still hardcoded into home.html
  _Fix:_ Removed static content and injected cards dynamically via JS and fetch API

- **/get_books/ returned 404**
  _Cause:_ Route was missing from books/urls.py
  _Fix:_ Added path 'get_books/' pointing to fetch_books view

- **fetch_books returned None instead of HttpResponse**
  _Cause:_ View was missing a return statement in some paths
  _Fix:_ Ensured JsonResponse is returned in all conditions, including except

- **TemplateSyntaxError: Unclosed {% block %} tag**
  _Cause:_ {% block content %} wasn’t closed before {% block scripts %}
  _Fix:_ Added proper {% endblock %} before the scripts section

- **JS didn’t run at all**
  _Cause:_ {% block scripts %} missing from base.html
  _Fix:_ Inserted {% block scripts %}{% endblock %} just before </body>

- **Some book thumbnails didn’t load**  
  _Cause:_ Missing or broken thumbnail URLs  
  _Fix:_ Added `onerror` fallback → `/static/img/book-placeholder.png`

- **Load More button appeared below footer**  
  _Cause:_ Rendered outside `.container`  
  _Fix:_ Repositioned inside container block below book grid

- **Search and filters not triggering correctly**  
  _Cause:_ Inconsistent event bindings  
  _Fix:_ Ensured consistent event handlers for search, Enter key, genre, and sort

- **Cards overflowed or stacked poorly on small screens**  
  _Cause:_ Missing mobile-specific breakpoints  
  _Fix:_ Adjusted Bootstrap column classes (`col-6 col-md-4 col-lg-3 col-xl-2`)

- **Global CSS styles not applied**  
  _Cause:_ CSS file not found or misconfigured  
  _Fix:_ Set `STATICFILES_DIRS` in `settings.py`, placed file in `static/books/css/style.css`, and included in `base.html`

- **Genre and Sort filters were misaligned**  
  _Cause:_ Lack of parent `.container` or incorrect flex wrapping  
  _Fix:_ Wrapped in Bootstrap container and used flexbox utilities

- **Add Book Search Not Working**

**Issue:** The Google Books search in the _Add Book_ page was not displaying any results.

**Cause:** The Django view `search_google_books` was returning a JSON response with key `results`, while the frontend JavaScript expected `data.books`.

**Fix:** Update the view to return `books` instead of `results`:

```python
# Before:
return JsonResponse({'results': books})

# After:
return JsonResponse({'books': books})
```

- **Login redirected to /accounts/profile/ instead of homepage**

  _Cause:_ Django’s default `LOGIN_REDIRECT_URL` not set  
  _Fix:_ Added `LOGIN_REDIRECT_URL = 'home'` to `settings.py`

- **Logout returned HTTP 405 error**

  _Cause:_ Django expects logout via POST, not GET  
  _Fix:_ Used a form for logout action instead of a direct link

- **Avatar crash: ValueError: The 'avatar' attribute has no file associated**

  _Cause:_ Accessing `avatar.url` when no file was uploaded  
  _Fix:_ Wrapped image in `{% if user.profile.avatar %}` conditional and added fallback

- **Mobile: 3-column layout on small screens**

  _Cause:_ Bootstrap grid did not break early enough  
  _Fix:_ Used responsive column classes like `col-6 col-md-4 col-lg-3` for proper stacking

- **TemplateDoesNotExist error for partials/profile_bio.html**
  _Cause:_ Referenced non-existent include file  
  _Fix:_ Embedded the bio form directly into `profile.html` and removed partial

- **Username/Email form not saving changes**

  _Cause:_ Django couldn’t detect which form was submitted

  _Fix:_ Added <input type="hidden" name="update_user_form" value="1"> and checked for 'update_user_form' in request.POST

- **Footer appeared too high on large screens**

  _Cause:_ Body did not use full-height layout

  _Fix:_ Wrapped <body> in d-flex flex-column min-vh-100 and applied flex-grow-1 to <main> for sticky footer behavior

- **Old avatars piling up in media folder**

  _Cause:_ Django keeps all uploaded files unless manually deleted

  _Fix:_ Added logic to remove the previous avatar file when a new one is uploaded

- **Default avatar deleted accidentally**

  _Cause:_ No check to protect default/fallback image

  _Fix:_ Skipped deletion if filename ends with avatar-placeholder.png

- **Large avatar uploads slowed down site**

  _Cause:_ Uploaded images could be high-res (3000x3000+) and 5MB+ in size

  _Fix:_ Compressed avatars to JPEG and resized them to 300x300px max using Pillow

- **Bio disappeared after avatar change**

  _Cause:_ Avatar upload form did not include existing bio, causing it to overwrite with blank

  _Fix:_ Passed current bio as a hidden input in the form

## These issues were identified during local development and resolved using Django’s documentation and testing.

## 3rd Party Services, APIs & Scripts

### 📘 Google Books API Integration

The pattern for dynamically fetching books and updating the DOM was adapted based on tutorials and AI support:

```js
fetch(`/get_books/?q=${encodeURIComponent(query)}&order=${sort}&startIndex=${startIndex}`)
  .then(response => response.json())
  .then(data => {
    // rendering logic
  });
Source: MDN Fetch API, ChatGPT guidance
```

### 🖼️ Fallback for Broken Book Covers

Displays a placeholder image if the cover URL is missing or broken:

```html
<img
  src="${book.thumbnail}"
  class="card-img-top"
  alt="Book Cover"
  onerror="this.onerror=null; this.src='/static/img/book-placeholder.png';"
/>
Based on solution from: Stack Overflow
```

### 🌀 Bootstrap Loading Spinner

Used to indicate that books are being fetched asynchronously:

```html
<div class="spinner-border text-primary" role="status">
  <span class="visually-hidden">Loading...</span>
</div>
Source: Bootstrap 5 Spinner Docs
```

➕ Load More Button Logic
Used to incrementally load batches of books via startIndex and toggle button visibility:

```js
if (data.books.length === batchSize) {
  loadMoreBtn.classList.remove('d-none');
}
Inspired by: JavaScript pagination patterns and ChatGPT
```

### 🧱 Responsive Grid with Bootstrap

Utilized Bootstrap’s responsive column layout to ensure book cards adjust to screen size:

```html
<div class="col-6 col-md-4 col-lg-3 col-xl-2 d-flex">
  <div class="card flex-fill shadow-sm">
    <!-- book content -->
  </div>
</div>
Source: Bootstrap 5 Grid System
```

---

### 📸 Pillow

Required for ImageField in Django models (user avatars). Installed via:

> pip install Pillow

### Bio Edit Toggle Script

Purpose:
This script is used to toggle between a user's displayed bio and an editable bio form on their profile page. Clicking "Edit" hides the static content and reveals the input form, while "Cancel" reverses the action.

Source:
Custom inline JavaScript inspired by standard DOM manipulation patterns.
Reference: MDN Web Docs – getElementById

```html
<script>
  function enablebioedit() {
    document.getElementById("bio-display").style.display = "none";
    document.getElementById("bio-form").style.display = "block";
  }

  function cancelbioedit() {
    document.getElementById("bio-form").style.display = "none";
    document.getElementById("bio-display").style.display = "block";
  }
</script>
```

---

All reused snippets were adapted and integrated with original code. The majority of the implementation is custom work tailored to the project goals.
