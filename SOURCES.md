# Data Source Technical Research Specs

Detailed breakdowns of the real-world enterprise data integration shapes used to validate the BreatheESG pipeline engine.

## 1. SAP ERP Procurement (Fuel Logistics)
* **Real-World Discovery**: Enterprise systems utilize technical German descriptors across layout fields. Standard inventory records map under abbreviations like `MATNR` (Material Number), `WERKS` (Plant Facility), `MENG` (Quantity), and `MEINS` (Base Unit of Measure).
* **Implementation Shape**:
  ```csv
  MENG,MEINS,WERKS,BUDAT
  5000,L,PL01,2026-05-15
  0,L,PL02,2026-05-16