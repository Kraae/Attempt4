
#Database Schema Documentation
##Tables and Fields
"""
Books (
- **Book_id (Primary Key)**
- **Title**: Title of the book
- **author**: author of the book
- **description**: description of the book
- **Thumbnail_url**: Thumbnail of the book
)
"""


   CREATE TABLE "book" (
      "id" serial PRIMARY KEY,
      "title" TEXT NOT NULL,
      "author" TEXT NOT NULL,
      "description" TEXT NOT NULL,
      "subjects" TEXT NOT NULL,
      "thumbnail_url" BLOB
      CONSTRAINT "pk_book" PRIMARY KEY(
         "id"
      )
   );
               
   CREATE TABLE "user" (
      id INTEGER PRIMARY KEY,
      "username" TEXT,
      "password" TEXT,
      CONSTRAINT "pk_user" PRIMARY KEY (
         "id"
      )
   );

   
