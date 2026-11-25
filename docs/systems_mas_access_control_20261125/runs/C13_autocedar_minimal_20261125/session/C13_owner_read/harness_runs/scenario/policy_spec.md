# AutoCedar Approved Intent Target

This Stage 3 specification is generated from HITL/AITL-approved schema and property atoms. The raw input document remains archived as `requirement.md` in the session input directory, but policy synthesis must satisfy the reviewed formal target below rather than reinterpreting the raw prose.

## Approved Schema Atoms
- supplied schema; no Stage 1 atoms

## Approved Property Atoms
- condition.0002.step0001 for scope.readDocument.User.Document [condition]: A user may read a document only when that user is the document's owner. (action=readDocument; principals=User; resources=Document; source_ids=src.root.p0002.l3; source=[source_id: src.root.p0002.l3] A user may read a document only when that user is the document's owner.)
- floor__scope_readdocument_user_document__slice_readdocument_user_document_1 [floor]: Requests in slice 'User may read a document only when the user is the document's owner.' must be allowed. (action=readDocument; principals=User; resources=Document; source_ids=src.root.p0002.l3; source=[source_id: src.root.p0002.l3])
- ceiling__scope_readdocument_user_document [ceiling]: Only requests in one of this scope's slices may be allowed. (action=readDocument; principals=User; resources=Document; source_ids=src.root.p0002.l3; source=[source_id: src.root.p0002.l3])
