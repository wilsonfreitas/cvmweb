
from datetime import date, datetime

import zeep
import zeep.exceptions

from cvmweb.util import download_unzip
from cvmweb.data import CVMWebData


## Known Fault messages:
#
# Usuário atingiu o número máximo de autorizações para download permitido. Autorização não concedida.
# Ocorreu um erro no processamento do WebMethod. Favor, entrar em contato com o suporte através do email suporte@cvm.gov.br, informando o código 'WS20140911_065647546'.
# Arquivo para download não encontrado para os parâmetros especificados
# Permissão negada. Por favor, efetue o login antes de acessar essa funcionalidade.
# Conversão do parâmetro strDtRefer para data não retorna dia útil.
# Conversão do parâmetro strDtComptcDoc para data não retorna dia útil.


class CVMWeb(object):
    WSDL = 'http://www.cvm.gov.br/webservices/Sistemas/SCW/CDocs/WsDownloadInfs.asmx?WSDL'
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = zeep.Client(self.WSDL)
        self.session = None
        self._login()

    def method_call(self, method, **parms):
        parms["_soapheaders"] = [self.session]
        return self.client.service[method](**parms)

    def get_url(self, method, **parms):
        result = self.method_call(method, **parms)
        meth = dir(result.body)[0]
        return result.body[meth]

    def _login(self):
        login = self.client.service.Login(iNrSist=self.username, strSenha=self.password)
        self.session = login.header


# métodos com autenticação
# cadastro / Cadastro / CADASTRO
# 'solicAutorizDownloadCadastro', parms={'strDtRefer': None}
# 
# balancete / Balancete / BALANCETE
# informediario / InformeDiario / INFORMEDIARIO / informe_diario / INFORME_DIARIO
## com data
# 'solicAutorizDownloadArqEntregaPorData', parms={'strDtEntregaDoc': None, 'iCdTpDoc': 209/50}
# 'solicAutorizDownloadArqComptc', parms={'strDtComptcDoc': None, 'iCdTpDoc': 209/50}
## sem data
# 'solicAutorizDownloadArqEntrega', parms={'iCdTpDoc': 209/50}
# 'solicAutorizDownloadArqAnual', parms={'iCdTpDoc': 209/50}
# 
# métodos sem autenticação
# 'retornaDtLmtEntrDocsArqsDisp', iCdTpDoc=209/50
# 'retornaListaComptcDocs', iCdTpDoc=209/50, strDtIniEntregDoc
# 'retornaListaComptcDocsPartic', iCdTpDoc=209/50, strDtIniEntregDoc, strNrPfPj
# 'retornaListaComptcDocsAdm', iCdTpDoc=209/50, strDtIniEntregDoc, strNrPfPj


class CVMWebService(CVMWeb):
    
    def __init__(self, username, password):
        super(CVMWebService, self).__init__(username, password)
    
    def get_info(self, code, info, refdate=None, cnpj=None):
        parms = {}
        if code == 'INFORME_DIARIO':
            parms.update(iCdTpDoc=209)
        elif code == 'BALANCETE':
            parms.update(iCdTpDoc=50)
        else:
            raise ValueError('Invalid code: {}'.format(code))
        if info == "DATA_LIMITE":
            res = self.method_call('retornaDtLmtEntrDocsArqsDisp', **parms)
            meth = dir(res.body)[0]
            return res.body[meth]
        elif info == "DATAS_COMP":
            refdate = refdate if refdate else date.today().isoformat()
            parms.update(strDtIniEntregDoc=refdate)
            res = self.method_call('retornaListaComptcDocs', **parms)
        elif info == "DATAS_COMP_FUNDO":
            refdate = refdate if refdate else date.today().isoformat()
            parms.update(strDtIniEntregDoc=refdate)
            parms.update(strNrPfPj=cnpj)
            res = self.method_call('retornaListaComptcDocsPartic', **parms)
        elif info == "DATAS_COMP_ADM":
            refdate = refdate if refdate else date.today().isoformat()
            parms.update(strDtIniEntregDoc=refdate)
            parms.update(strNrPfPj=cnpj)
            res = self.method_call('retornaListaComptcDocsAdm', **parms)
        meth = dir(res.body)[0]
        return res.body[meth].string

    def get_data(self, code, **parms):
        # code: CADASTRO, BALANCETE, INFORME_DIARIO
        if code == 'CADASTRO':
            return CVMWebData(self._get_cadastro(**parms))
        elif code == 'INFORME_DIARIO':
            parms.update(doctype=209)
            return CVMWebData(self._get_arq(**parms))
        elif code == 'BALANCETE':
            parms.update(doctype=50)
            return CVMWebData(self._get_arq(**parms))
        else:
            raise ValueError('Invalid code: {}'.format(code))
        
    def _get_cadastro(self, refdate=None):
        refdate = refdate if refdate else date.today().isoformat()
        url = self.get_url('solicAutorizDownloadCadastro', strDtRefer=refdate)
        return download_unzip(url)

    def _get_arq(self, refdate=None, type='daily', doctype=209):
        if type == 'annual':
            url = self.get_url('solicAutorizDownloadArqAnual', iCdTpDoc=doctype)
        elif type == 'final':
            refdate = refdate if refdate else date.today().isoformat()
            url = self.get_url('solicAutorizDownloadArqComptc', strDtComptcDoc=refdate, iCdTpDoc=doctype)
        elif type == 'daily':
            if refdate:
                refdate = refdate if refdate else date.today().isoformat()
                url = self.get_url('solicAutorizDownloadArqEntregaPorData', strDtEntregaDoc=refdate, iCdTpDoc=doctype)
            else:
                url = self.get_url('solicAutorizDownloadArqEntrega', iCdTpDoc=doctype)
        else:
            ValueError('Invalid type {}'.format(type))
        return download_unzip(url)


