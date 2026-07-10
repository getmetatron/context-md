# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When manipulating Sphinx nodes, always check the parent node's structure (e.g., `contentnode.parent[0]`) to reliably access context information like the signature node.
- [2026-07-10] When modifying docutils nodes, be mindful of how content is appended or inserted; using `node.insert()` or `node +=` requires understanding the node's current contents and desired placement relative to existing elements.
- [2026-07-10] Type hint processing often requires handling multiple object types (e.g., callable vs. descriptor) separately, as the inspection mechanism (`inspect.signature`) differs significantly between them.
