import json

from django.conf import settings

from web3 import Web3
from web3.exceptions import ContractLogicError


provider_url = f'{settings.BASE_PROVIDER_URL}{settings.PROVIDER_API_KEY}'

web3 = Web3(Web3.HTTPProvider(provider_url))


def get_gas_price():
    """
    Возвращает актуальную цену на газ.
    """
    return web3.eth.gas_price


def get_nonce(address):
    """
    Возвращает nonce кошелька пользователя.

    :param address: адрес крипто кошелька
    """
    return web3.eth.get_transaction_count(address)


def normalize_address(address):  # pragma: no cover
    """
    Нормализует, если возможно, переданную последовательность в блокчейн адрес.

    :param address: адрес крипто кошелька/смарт-контракта
    """
    return Web3.to_checksum_address(address.strip().lower())


def get_nft_contract():
    """
    Получение объекта смарт-контракта MintableNFT.
    """
    with open(f'{settings.BLOCKCHAIN_SOURCE_PATH}/MintableNFT.json') as f:
        abi = json.load(f)

    contract = web3.eth.contract(address=settings.NFT_CONTRACT_ADDRESS, abi=abi)

    return contract


def read_contract(contract, method_name, *args, **kwargs):
    """
    Базовый метод чтения контракта.

    :param contract: объект контракта
    :type web3.contract:
    :param sender: вызываемый метод
    """
    if not hasattr(contract.functions, method_name):
        raise ValueError(F'Incorrect contract method: {method_name}')

    method = getattr(contract.functions, method_name)

    return method(*args).call()


def get_write_tx(contract, sender, method_name, *args, **kwargs):
    """
    Возвращает транзакцию для запуска метода смарт-контракта.

    :param contract: объект контракта
    :type web3.contract:
    :param sender: адрес инициатора операции
    :param method_name: запускаемый метод смарт-контракта
    :params args: параметры для вызова метода смарт-контракта
    """
    transaction, created = None, False

    if not hasattr(contract.functions, method_name):
        raise ValueError(f'Incorrect contract method: {method_name}')

    method = getattr(contract.functions, method_name)
    address = normalize_address(sender)

    try:
        transaction = method(*args).build_transaction({
            'from': address,
            'nonce': get_nonce(sender),
            'gasPrice': get_gas_price(),
            'gas': 250000,
        })
    except ContractLogicError as err:
        return transaction, created

    created = True

    return transaction, created


def send_tx(tx, deployer_secret=settings.DEPLOYER_SECRET):
    """
    Отправляет подписанную транзакцию на исполнение.

    :param tx: транзакция
    :param deployer_secret: приватный ключ инициатора вызова функции
    """
    signed_transaction = web3.eth.account.sign_transaction(tx, deployer_secret)
    tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)

    return tx_hash.hex()


def mint_nft(*args, **kwargs):
    """
    Вызов функции mint.
    """
    contract = get_nft_contract()
    sender = settings.DEPLOYER_ADDRESS

    transaction, created = get_write_tx(
        contract,
        sender,
        'mint',
        *args,
        **kwargs,
    )

    tx_hash = send_tx(transaction)

    return tx_hash


def get_total_supply(contract, *args, **kwargs):
    """
    Вызов метода totalSupply.
    """
    return read_contract(contract, 'totalSupply', *args, **kwargs)
