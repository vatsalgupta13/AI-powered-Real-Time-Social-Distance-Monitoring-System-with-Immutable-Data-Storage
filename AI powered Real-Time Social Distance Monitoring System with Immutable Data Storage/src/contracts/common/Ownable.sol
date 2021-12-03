pragma solidity ^0.6.1;

//import "../interfaces/IERC173.sol";

contract Ownable {
    address internal _owner;

    event LogOwnershipTransferred(address indexed _currentOwner, address indexed _newOwner);

    modifier onlyOwner() {
        require(msg.sender == _owner, "The owner should be the sender");
        _;
    }

    constructor() public {
        _owner = msg.sender;
        //emit OwnershipTransferred(address(0x0), msg.sender);
        emit LogOwnershipTransferred(address(0x0), msg.sender);
    }

    function owner() external view returns (address) {
        return _owner;
    }

    /**
        @dev Transfers the ownership of the contract.
        @param _newOwner Address of the new owner
    */
    function transferOwnership(address _newOwner) external onlyOwner {
        require(_newOwner != address(0), "0x0 Is not a valid owner");
        //emit OwnershipTransferred(_owner, _newOwner);
        emit LogOwnershipTransferred(_owner, _newOwner);
        _owner = _newOwner;
    }
}
