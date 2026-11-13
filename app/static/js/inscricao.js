(() => {
  const form = document.getElementById('form-inscricao');
  const cpf = document.getElementById('cpf');
  const telefone = document.getElementById('telefone');
  const matricula = document.getElementById('matricula');
  const button = document.getElementById('enviar-inscricao');
  if (!form) return;

  const digits = value => value.replace(/\D/g, '');
  const maskCpf = value => {
    const d = digits(value).slice(0, 11);
    return d.replace(/^(\d{3})(\d)/, '$1.$2').replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3').replace(/\.(\d{3})(\d)/, '.$1-$2');
  };
  const maskPhone = value => {
    const d = digits(value).slice(0, 11);
    if (d.length <= 2) return d ? `(${d}` : '';
    if (d.length <= 6) return `(${d.slice(0,2)}) ${d.slice(2)}`;
    if (d.length <= 10) return `(${d.slice(0,2)}) ${d.slice(2,6)}-${d.slice(6)}`;
    return `(${d.slice(0,2)}) ${d.slice(2,7)}-${d.slice(7)}`;
  };

  cpf.addEventListener('input', () => { cpf.value = maskCpf(cpf.value); });
  telefone.addEventListener('input', () => { telefone.value = maskPhone(telefone.value); });
  matricula.addEventListener('input', () => { matricula.value = matricula.value.toUpperCase().replace(/[^A-Z0-9.\-]/g, ''); });
  cpf.value = maskCpf(cpf.value);
  telefone.value = maskPhone(telefone.value);

  form.addEventListener('submit', event => {
    if (digits(cpf.value).length !== 11) {
      cpf.setCustomValidity('Informe os 11 dígitos do CPF.');
    } else cpf.setCustomValidity('');
    if (![10,11].includes(digits(telefone.value).length)) {
      telefone.setCustomValidity('Informe um telefone com DDD.');
    } else telefone.setCustomValidity('');
    if (!form.reportValidity()) { event.preventDefault(); return; }
    button.disabled = true;
    button.textContent = 'Enviando inscrição...';
  });
  cpf.addEventListener('input', () => cpf.setCustomValidity(''));
  telefone.addEventListener('input', () => telefone.setCustomValidity(''));
})();
