import random

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'sua_chave_muito_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    saldo = db.Column(db.Float, default=0.00)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/depositar')
@login_required
def depositar_page():
    return render_template('depositar.html', saldo=current_user.saldo)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')

    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'danger')
            return redirect(url_for('cadastro'))

        novo_usuario = User(username=username)
        novo_usuario.set_password(password)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça o login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('index'))

@app.route('/adicionar_saldo', methods=['POST'])
@login_required
def adicionar_saldo():
    try:
        valor = float(request.form.get('valor'))
        if valor > 0:
            current_user.saldo += valor
            db.session.commit()
            flash(f'R${valor:.2f} adicionados com sucesso.', 'success')
        else:
            flash('O valor deve ser positivo.', 'danger')
    except ValueError:
        flash('Valor inválido.', 'danger')
    
    return redirect(url_for('depositar_page'))

@app.route('/coin_flip', methods=['GET', 'POST'])
@login_required
def coin_flip():
    resultado_jogo = None

    if request.method == 'POST':
        try:
            aposta_str = request.form.get('aposta')
            escolha = request.form.get('escolha')
            
            aposta = float(aposta_str)
            if aposta <= 0:
                flash('A aposta deve ser um valor positivo.', 'danger')
                return redirect(url_for('coin_flip'))
            
            if aposta > current_user.saldo:
                flash('Saldo insuficiente para esta aposta.', 'danger')
                return redirect(url_for('coin_flip'))

            lados = ['cara', 'coroa']
            resultado_lancamento = random.choice(lados)
            
            if escolha == resultado_lancamento:
                current_user.saldo += aposta
                flash(f'Parabéns! Deu {resultado_lancamento}. Você ganhou R${aposta:.2f}!', 'success')
                resultado_jogo = {'lancamento': resultado_lancamento, 'vitoria': True, 'aposta': aposta}
            else:
                current_user.saldo -= aposta
                flash(f'Que pena! Deu {resultado_lancamento}. Você perdeu R${aposta:.2f}.', 'danger')
                resultado_jogo = {'lancamento': resultado_lancamento, 'vitoria': False, 'aposta': aposta}

            db.session.commit()

        except ValueError:
            flash('Valor de aposta inválido.', 'danger')
        except Exception as e:
            flash(f'Ocorreu um erro no jogo: {e}', 'danger')
            
    return render_template('coin_flip.html', resultado_jogo=resultado_jogo)

@app.route('/simple_roulette', methods=['GET', 'POST'])
@login_required
def simple_roulette():
    resultado_jogo = None
    
    if request.method == 'POST':
        try:
            aposta_str = request.form.get('aposta')
            escolha = request.form.get('escolha')
            
            aposta = float(aposta_str)
            if aposta <= 0:
                flash('A aposta deve ser um valor positivo.', 'danger')
                return redirect(url_for('simple_roulette'))
            
            if aposta > current_user.saldo:
                flash('Saldo insuficiente para esta aposta.', 'danger')
                return redirect(url_for('simple_roulette'))

            resultado_roleta = random.randint(0, 36)
            ganhou = False
            
            if resultado_roleta == 0:
                ganhou = False
            elif resultado_roleta % 2 == 0 and escolha == 'par':
                ganhou = True
            elif resultado_roleta % 2 != 0 and escolha == 'impar':
                ganhou = True
            else:
                ganhou = False
                
            if ganhou:
                current_user.saldo += aposta
                flash(f'Parabéns! O número sorteado foi {resultado_roleta}. Você ganhou R${aposta:.2f}!', 'success')
            else:
                current_user.saldo -= aposta
                flash(f'Que pena! O número sorteado foi {resultado_roleta}. Você perdeu R${aposta:.2f}.', 'danger')

            db.session.commit()
            
            resultado_jogo = {
                'lancamento': resultado_roleta, 
                'vitoria': ganhou, 
                'aposta': aposta,
                'escolha_usuario': escolha
            }

        except ValueError:
            flash('Valor de aposta inválido.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro no jogo: {e}', 'danger')
            
    return render_template('simple_roulette.html', resultado_jogo=resultado_jogo)

SIMBOLOS = ['💎', '🍒', '🍋']
PAGAMENTOS = {
    ('💎', '💎', '💎'): 10,
    ('🍒', '🍒', '🍒'): 5,
    ('🍋', '🍋', '🍋'): 3,
}

@app.route('/slot_machine', methods=['GET', 'POST'])
@login_required
def slot_machine():
    resultado_jogo = None
    
    if request.method == 'POST':
        try:
            aposta_str = request.form.get('aposta')
            aposta = float(aposta_str)
            
            if aposta <= 0:
                flash('A aposta deve ser um valor positivo.', 'danger')
                return redirect(url_for('slot_machine'))
            
            if aposta > current_user.saldo:
                flash('Saldo insuficiente para esta aposta.', 'danger')
                return redirect(url_for('slot_machine'))

            cilindro1 = random.choice(SIMBOLOS)
            cilindro2 = random.choice(SIMBOLOS)
            cilindro3 = random.choice(SIMBOLOS)
            
            resultado_simbolos = (cilindro1, cilindro2, cilindro3)
            
            multiplicador = PAGAMENTOS.get(resultado_simbolos, 0)
            
            ganho_liquido = 0
            
            if multiplicador > 0:
                ganho_liquido = aposta * multiplicador
                current_user.saldo += ganho_liquido
                flash(f'🎊 VITÓRIA! {multiplicador}x a aposta. Você ganhou R${ganho_liquido:.2f}!', 'success')
            else:
                current_user.saldo -= aposta
                ganho_liquido = -aposta
                flash(f'💔 Você perdeu R${aposta:.2f}. Tente novamente!', 'danger')

            db.session.commit()
            
            resultado_jogo = {
                'simbolos': resultado_simbolos, 
                'ganho_liquido': ganho_liquido, 
                'aposta': aposta,
                'vitoria': ganho_liquido > 0
            }

        except ValueError:
            flash('Valor de aposta inválido.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocorreu um erro no jogo: {e}', 'danger')
            
    return render_template('slot_machine.html', resultado_jogo=resultado_jogo, simbolos_possiveis=SIMBOLOS)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)