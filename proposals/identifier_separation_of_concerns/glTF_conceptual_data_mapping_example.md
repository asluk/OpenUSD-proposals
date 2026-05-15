---
orphan: true
---

# Example: glTF and OpenUSD Conceptual Data Mapping

```{important}
**{octicon}`tag;1em` Template Version:** {bdg-secondary}`1.0.0` 
<br>**{octicon}`calendar;1em` Last Update:** {bdg-secondary}`2024-09-18`
    
You can download the Markdown for {download}`this example conceptual data mapping document <./glTF_conceptual_data_mapping_example.md>` to use as a starting point for your own document.
```

## Introduction

### Overview
Overview text

### References
This document has been prepared in reference to the software or specification versions listed below. Adjustments or considerations may need to be made for previous or future versions than those referenced in this document.

#### glTF Reference
| Version | Reference Documents  |
|---|---|    
|2.0.1|[glTF 2.0 Specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), [glTF Quickstart Guide](https://www.khronos.org/files/gltf20-reference-guide.pdf)|    


#### OpenUSD Reference

| Version | Reference Documents  |
|---|---|    
| 24.08  | [OpenUSD C++ and Schema Documentation](https://openusd.org/release/api/index.html), [OpenUSD Github Repository](https://github.com/PixarAnimationStudios/OpenUSD), [USD Terms and Concepts](https://openusd.org/release/glossary.html)  |     


### General Assumptions and Constraints
#### Node Names and Node Collapsing
A node in glTF is very similar to a prim in OpenUSD, but the functionality of single prim can often be mapped to multiple nodes that work together in glTF. When translating to OpenUSD, we propose collapsing multiple nodes into a single corresponding OpenUSD prim type. When collapsing nodes, a node name from the group of collapsed nodes must be chosen for the prim. Refer to [Appendix B: Node Name](#appendix-b-node-name) for more details.

#### Path Encoding
Explanation about path encoding. Refer to [Appendix A: Path Encoding](#appendix-a-path-encoding) for more details.

### Definitions, Acronyms, Abbreviations
Define terms used in this document. They could come from one of the source formats and be presented here for reader convenience. No need for establishing mappings for these in this table.

| Term or Abbreviation | Description |
|---|---|    
| scenegraph  |  A data structure that organizes a graphical scene's logical and spatial representation as a tree or graph of nodes. |     
|   |   |

## Concepts
You can include introduction/overview text here. Then followed by a table showing high-level concept mappings. List all concepts from X even if there is no direct mapping or support for the feature in OpenUSD. If the concept doesn’t exist or map to OpenUSD, leave the OpenUSD cell blank and briefly explain in the Description.

Not required, but beneficial for Two-Way translation, also list all OpenUSD concepts even if there is no direct mapping or support for a feature in X. If the concept doesn’t exist or map to X, leave the X cell blank and briefly explain in the Description. You can link the OpenUSD cell to a drilldown section to explain the limitation in more detail.

| glTF | OpenUSD | Description |
|---|---|---|
|[Scenes](#scenes)|Stage| Represents a scenegraph. More details in the [drilldown](#scenes).|
|[Nodes](#nodes)|Prim Hierarchy|A collection of nodes that make up a scenegraph.|

### Scenes
In glTF, Scenes in conjunction with [Nodes](#nodes) are used to represent a scenegraph. A Scene is analogous to a Stage in USD which represents a composed scenegraph. One big divergence between the two to account is that a glTF document can store zero, one, or many scenes. We believe one scene per document provides more clear intent and recommend that as a best practice, but if you would like to support translating multiple scenegraphs to USD, see the [Composition](#composition) section for some recommendations on how to reconcile multiple scenegraphs in USD.

#### Properties
| glTF | OpenUSD | Description |
|---|---|---|
|[foo](#property-foo)|usd_foo| |
|bar|usd_bar| |

##### Property: foo
More info about the property and any data transformations that should be applied.

| | Name | Data Type |
|---|---|---|
|glTF|foo| float |
|OpenUSD|usd_foo| float |

#### Metadata

#### Composition

##### Multiple scenes per document

###### Variant Sets
Consider using a Variant Set on the default prim to support multiple scenes from a glTF document. Each scene could be represented as a variant with the scene property in glTF used as the default variant selection in USD.

|Pros|Cons|
|---|---|
| | |
| | |

###### Dynamic Payload
Alternatively, if you are developing a File Format Plugin or a Dynamic Payload, the scene property could be used as an argument for a Dynamic Payload so that end users can specify the scene they want loaded via Dynamic Payload arguments.

|Pros|Cons|
|---|---|
| | |
| | |

### Nodes
This is a section describing the Nodes concept.

#### Properties

| glTF | OpenUSD | Description |
|---|---|---|
| | | |
| | | |

#### Metadata

#### Composition

## Appendices

### Appendix A: Path Encoding

### Appendix B: Node Name