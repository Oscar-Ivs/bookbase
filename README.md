
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
- Search for books using a built-in interface *(planned)*
- View book details, but cannot modify or comment

## 🔮 Future Features

BookBase is designed to evolve. Planned enhancements include:
- User registration and individual collections
- Role-based permissions (e.g., moderators, admins)
- Public/private toggle for each user’s collection
- Commenting on public book entries *(for registered users only)*
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
  Stores book data fetched from the Google Books API or manually entered *(planned feature)*.

- **UserBook**  
  Connects users to books they've added to their personal collection.

- **Note**  
  Allows users to attach private notes to books in their collection.

- **Comment** *(future feature)*  
  Enables users to leave public comments on books.

> 💡 *If a book is not found via Google Books, future versions may allow manual entry including cover uploads.*

![BookBase ERD](docs/erd/bookbase_erd.png)


This structure supports all core CRUD operations and prepares the project for future features such as user accounts and comment management.
---

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


---

## Troubleshooting & Known Fixes

While developing BookBase, several key issues were encountered and resolved:

- **Login redirected to `/accounts/profile/` instead of homepage**  
  *Cause:* Django's `LoginView` defaults to `/accounts/profile/`  
  *Fix:* Added `LOGIN_REDIRECT_URL = 'home'` to `settings.py`

- **Logout returned HTTP 405 error**  
  *Cause:* Logout was triggered via a `GET` request; Django expects `POST`  
  *Fix:* Replaced direct `<a>` logout link with a form using `POST` method

- **`NoReverseMatch` errors for views like `home`, `about`, `profile`**  
  *Cause:* View names used in `base.html` didn't exist yet  
  *Fix:* Created placeholder views in `views.py` and linked them in `urls.py`

  - **Cover image URL caused validation or 502 error**
Cause: Using right-click → "Copy image address" from Google Images often gives base64 or unusable proxies
Fix: Used clean direct image URLs (e.g. from OpenLibrary or Goodreads cover images)

- **Social links in footer showed unexpected _ character**
Cause: Font Awesome misrendering or extra whitespace - still not solved, left for later
Fix: Tweaked <i> tags and surrounding layout with spacing classes (gap-3, align-items-center, etc.)

- **Footer elements not aligned**
Cause: Text and icons stacked vertically by default
Fix: Used Bootstrap's flex utilities to align items side-by-side and justify space between

These issues were identified during local development and resolved using Django’s documentation and testing.
---
