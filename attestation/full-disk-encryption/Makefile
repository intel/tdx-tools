.PHONY: all clean 

all: 
	cargo build --release
	strip --strip-all target/release/fde-agent
	
clean:
	cargo clean
	