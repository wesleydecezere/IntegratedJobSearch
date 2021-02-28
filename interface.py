"""
    Inegrated Job Search
    @author Wesley Decezere
"""

from tkinter import *
from tkinter.ttk import *
from tkhtmlview import *
from tkinter import messagebox as mb

from indeed import *
from infojobs import *

class Interface:
    def __init__(self, master=None):
        # Estados disoníveis
        self.uf_initials = [
            '', 'AC', 'AL', 'AP', 'AM', 'BA',
            'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB',
            'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP',
            'SE', 'TO'
           ]
        self.uf_name = [
            '', 'Acre', 'Alagoas',  'Amapá', 'Amazonas', 'Bahia',
            'Ceará', 'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão',
            'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará', 'Paraíba',
            'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro', 'Rio Grande do Norte',
            'Rio Grande do Sul', 'Rondônia', 'Roraima', 'Santa Catarina', 'São Paulo',
            'Sergipe', 'Tocantins'
            ]
        self.uf = {x:y for x,y in zip(self.uf_initials, self.uf_name)}

        # Filtros de pesquisa
        self.op = dict()

        # Dataframe com resultados de pesquisa
        self.df = 0

        # seleção do portal
        self.stCont = Frame(master)
        #self.stCont.grid(row=0, pady=5)
        self.stCont.pack(pady=5, expand=1)

        self.portal_label = Label(self.stCont)
        self.portal_label['text'] = 'Portais disponíveis'
        self.portal_label.grid(row=0, column=0)
        self.portal_op = Combobox(self.stCont)
        self.portal_op['state'] = "readonly"
        self.portal_op['values'] = ['', 'Infojobs', 'Indeed', 'Todos']
        self.portal_op['justify'] = "center"
        self.portal_op.grid(row=1)

        self.space1 = Label(self.stCont, width=4)
        self.space1.grid(row=1, column=1)

        # inserção do cargo
        self.position_label = Label(self.stCont)
        self.position_label['text'] = 'Cargo'
        self.position_label.grid(row=0, column=2, sticky=E)
        self.position_op = Entry(self.stCont)
        self.position_op.grid(row=0, columnspan=2, column=3, sticky=W)

        # inserção do estado
        self.state_label = Label(self.stCont)
        self.state_label['text'] = 'UF'
        self.state_label.grid(row=1, column=2, sticky=E)
        self.state_op = Combobox(self.stCont, width=17)
        self.state_op['state'] = "readonly"
        self.state_op['values'] = self.uf_initials
        self.state_op.grid(row=1, columnspan=2, column=3, sticky=W)

        # inserção da cidade
        self.city_label = Label(self.stCont)
        self.city_label['text'] = 'Cidade'
        self.city_label.grid(row=2, column=2, sticky=E)
        self.city_op = Entry(self.stCont, width=20)
        self.city_op.grid(row=2, columnspan=2, column=3, sticky=W)

        # inserção do nro mínimo de resultados por portal
        self.nbr_label = Label(self.stCont)
        self.nbr_label['text'] = 'Resultados/portal'
        self.nbr_label.grid(row=0, column=5)
        self.nbr_op = Spinbox(self.stCont, from_=1, to=1000, width=8)
        self.nbr_op.set(0)
        self.nbr_op.grid(row=1, column=5, padx=30)

        # botão de busca
        self.ok = Button(self.stCont)
        self.ok['text'] = 'Buscar'
        self.ok['command'] = self.search
        self.ok['width'] = 15
        self.ok.grid(row=0, column=7)

        # botão de exibir resultados
        self.show_btn = Button(self.stCont)
        self.show_btn['text'] = 'Exibir resultados'
        self.show_btn['command'] = self.show
        self.show_btn['state'] = 'disabled'
        self.show_btn['width'] = 15
        self.show_btn.grid(row=1, column=7)

        # botão de salvar
        self.save_btn = Button(self.stCont)
        self.save_btn['text'] = 'Salvar resultados'
        self.save_btn['command'] = self.save
        self.save_btn['state'] = 'disabled'
        self.save_btn['width'] = 15
        self.save_btn.grid(row=2, column=7)

        # Espaço entre containers
        '''self.cont = Label(master)
        self.cont.pack()'''

        # Exibição dos resultados
        self.ndCont = Frame(master)
        self.ndCont.pack(expand=1)

        # vagas
        self.vacancy_label = Label(self.ndCont, text='Vagas')
        self.vacancy_label.grid(row=0, column=0)
        self.vacancy_lb = Listbox(self.ndCont, height=15, width=45)
        self.vacancy_lb.bind('<<ListboxSelect>>', self.show_details)
        self.vacancy_lb.grid(row=1, rowspan=15, column=0)

        self.scroll = Scrollbar(self.ndCont, command=self.vacancy_lb.yview)
        self.vacancy_lb.config(yscrollcommand=self.scroll.set)
        self.scroll.grid(row=1, rowspan=15, column=1, sticky=N+S+W)

        # demais campos (empresa, localização, data e link)
        self.company_label = Label(self.ndCont, text='Empresa')
        self.location_label = Label(self.ndCont, text='Lcalização')
        self.date_label = Label(self.ndCont, text='Data de publicação')
        self.link_label = Label(self.ndCont, text='Link')
        self.company_label.grid(row=0, column=3, sticky=W)
        self.location_label.grid(row=3, column=3, sticky=W)
        self.date_label.grid(row=6, column=3, sticky=W)
        self.link_label.grid(row=9, column=3, sticky=W)

        self.company_lb = Listbox(self.ndCont, height=1, width=40)
        self.location_lb = Listbox(self.ndCont, height=1, width=40)
        self.date_lb = Listbox(self.ndCont, height=1, width=40)
        self.link_txt = HTMLText(self.ndCont, height=6, width=40, font=('Arial', 8))
        self.company_lb.grid(row=1, column=3)
        self.location_lb.grid(row=4, column=3)
        self.date_lb.grid(row=7, column=3)
        self.link_txt.grid(row=10, column=3, rowspan=6)

        self.space2 = Label(self.ndCont, width=5)
        self.space2.grid(row=1, column=2)

    def search(self):
        if type(self.df) == int:
            mb.showwarning("Alerta",
                           "Ao inicar a busca, a janela ficará travada.\n"
                           "Esta mensagem só será exibida uma vez.\n\n"
                           "Pressione OK para continuar.")

        self.op['portal'] = self.portal_op.get()
        self.op['position'] = self.position_op.get()
        self.op['state'] = self.uf[self.state_op.get()]
        self.op['city'] = self.city_op.get()
        self.op['nbr'] = int(self.nbr_op.get())

        if self.op['portal'] == 'Infojobs':
            self.df = infojobs(self.op)
        elif self.op['portal'] == 'Indeed':
            self.df = indeed(self.op)
        elif self.op['portal'] == 'Todos':
            self.df = infojobs(self.op)
            self.df = pd.concat([self.df, indeed(self.op)], ignore_index=True)

        mb.showinfo("Notificação",
                    "A pesquisa foi finalizada com sucesso!\n\n"
                    "Pressione OK para liberar os outros comandos.")

        self.show_btn['state'] = 'normal'
        self.save_btn['state'] = 'normal'

    def show(self):
        self.vacancy_lb.delete(0, END)
        for i in range(len(self.df)):
            c = self.df.loc[i, 'vacancy']
            self.vacancy_lb.insert(i+1, c)

    def show_details(self, event):
        i = list(self.vacancy_lb.curselection())[0]
        vacancy = self.df.loc[i, 'vacancy']
        company = self.df.loc[i, 'company']
        location = self.df.loc[i, 'location']
        date = self.df.loc[i, 'date']
        link = self.df.loc[i, 'link']

        # exibe o link da vaga selecionada
        self.link_txt.delete(CURRENT, END)
        self.link_txt.set_html(html="<a href="+link+">"+vacancy+"</a>")

        # exibe a empresa da vaga selecionada
        self.company_lb.delete(0)
        self.company_lb.insert(0, company)

        # exibe a localização da vaga selecionada
        self.location_lb.delete(0)
        self.location_lb.insert(0, location)

        # exibe a data da vaga selecionada
        self.date_lb.delete(0)
        self.date_lb.insert(0, date)

    def save(self):
        try:
            with pd.ExcelWriter(self.op['position'] + '.xlsx', mode='a') as writer:
                self.df.to_excel(writer, sheet_name=self.op['portal'])
        except FileNotFoundError:
            with pd.ExcelWriter(self.op['position'] + '.xlsx', mode='w') as writer:
                self.df.to_excel(writer, sheet_name=self.op['portal'])

        mb.showinfo("Notificação",
                    "Os dados foram armazenados com sucesso!\n"
                    "Podem ser econtrados no arquivo '"+self.op['position']+".xls'\n\n"
                    "Pressione OK para continuar.")

root = Tk()  # instanciar a classe
root.title("Integrated Job Searcher")
root.resizable(width=FALSE, height=FALSE)

Interface(root)  # rodar a aplicação
root.mainloop()  # exibição da janela
