# cvmweb

cvmweb is a client for the CVM <http://www.cvm.gov.br> webservices of funds information.

```python
import cvmweb

username = xxxx
password = ****
service = cvmweb.CVMWebService(username, password)

data = service.get_data("INFORME_DIARIO")
print(data.xml)
```

```
<ROOT><CABECALHO><DT_REFER>2018-02-17</DT_REFER><DT_GERAC>2018-02-18 03:03:45</DT_GERAC><TP_REFER>DtEntregaDoc</TP_REFER></CABECALHO>...
```
