from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Union 



# in caso di rispostas del modello con reasoning, voglio un output di classificazione e una struttura di dict valida (che rappresenta l'attraversamento del grafo) 
"""
Schema JSON con Literal[0, 1]: ideale se vuoi anche spiegazioni, confidenza o più etichette insieme.

max_new_tokens=1 + prefix_allowed_tokens_fn + TypeAdapter: garantisce matematicamente un output 0 o 1 al 100% senza possibilità di errore sintattico e con latenza minima.
"""

#internal node rappresenta l'albero
class LeafNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node: str

class InternalNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node: str
    children: list[Union[InternalNode, LeafNode]]  = Field(min_length=1)


class BinaryClassification(BaseModel):
    label: Literal[0, 1] = Field(
        description="1 if the video supports a conspiracy theory, 0 otherwise"
    )

class TreeBinaryClassification(BaseModel):
    label: Literal[0, 1] = Field(
            description="1 if the video supports a conspiracy theory, 0 otherwise"
    )
    tree_path: InternalNode

InternalNode.model_rebuild()
