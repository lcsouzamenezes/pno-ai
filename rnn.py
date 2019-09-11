import argparse
from preprocess import PreprocessingPipeline
from train import train
from model import MusicRNN

def main():
    parser = argparse.ArgumentParser("Script to train a music-generating RNN on piano MIDI data")
    parser.add_argument("--test", action='store_true',
            help="if true, use a smaller data set")
    parser.add_argument("--pack_batches", action='store_true',
            help="if true, pack batches with sequences of variable length, else just pad.")
    parser.add_argument("--batch_size", type=int, default=20,
            help="number of sequences per batch")
    parser.add_argument("--lr", type=float, default=1,
            help="initializes model's learning rate")

    args = parser.parse_args()

    if args.test:
        print("Using smaller testing dataset...")
        input_dir = "data/test" 
        training_val_split = 0.7
    else:
        input_dir = "data/maestro-v2.0.0"
        training_val_split = 0.9

    #defines, in Hz, the smallest timestep preserved in quantizing MIDIs
    #determines number of timeshift events
    sampling_rate = 125
    #determines number of velocity events
    n_velocity_bins = 32
    pipeline = PreprocessingPipeline(input_dir=input_dir, stretch_factors=[0.95, 0.975, 1, 1.025, 1.05],
            split_size=30, sampling_rate=sampling_rate, n_velocity_bins=n_velocity_bins,
            transpositions=range(-3,4), training_val_split=training_val_split, sequence_length=(33,513))


    pipeline.run()
    training_sequences = pipeline.encoded_sequences['training']
    validation_sequences = pipeline.encoded_sequences['validation']
    n_states = 256 + sampling_rate + n_velocity_bins
    hidden_size = 128
    pack_batches = args.pack_batches
    rnn = MusicRNN(n_states, hidden_size, batch_first = not(pack_batches))
    train(rnn, training_sequences, validation_sequences, epochs = 2,  
            lr=args.lr, evaluate_per=1, batch_size=args.batch_size, pack_batches=pack_batches)

if __name__ == "__main__":
    main()
